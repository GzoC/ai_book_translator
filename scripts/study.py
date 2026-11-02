"""Measure the six authored fixtures with Tesseract and a cached, real Marian model."""

import argparse
import json
import os
import platform
import time
from collections import Counter
from importlib.metadata import version
from pathlib import Path
from threading import Event, Thread

import psutil
import pymupdf
import pytesseract
import torch

from technical_review.cli import write_review
from technical_review.extract import extract
from technical_review.quality import NUMBER, UNIT
from technical_review.translate import MarianTranslator


def expected_pages():
    # Transcription of the authored documents, independent of the extractor and OCR.
    digital = [
        "Power supply specification",
        "Rated voltage: 24 V. Rated current: 5 A.",
        "Inspect the circuit breaker before maintenance.",
    ]
    image = ["Pressure sensor", "Rated voltage: 24 V", "Measuring range: 0 to 10 bar"]
    return {
        "digital": [digital],
        "scanned": [image],
        "mixed": [digital + image],
        "table": [["Parameter", "Value", "Voltage", "24 V", "Current", "5 A"]],
        "equation": [["Electrical relationship", "P = V * I"]],
        "long": [
            [
                f"Inspection record {n}: verify the sensor and wiring."
                for n in range(start, start + 40)
            ]
            for start in (1, 41, 81)
        ],
    }


def norm(text):
    return " ".join(text.split())


def coverage(data, reference):
    missing, unexpected = [], []
    for page, lines in zip(data["pages"], reference, strict=True):
        observed = Counter(
            norm(line) for b in page["blocks"] for line in b["text"].splitlines()
        )
        gold = Counter(lines)
        for counter, errors in (
            (gold - observed, missing),
            (observed - gold, unexpected),
        ):
            errors.extend(
                {"page": page["number"], "line": line} for line in counter.elements()
            )
    return {
        "expected_lines": sum(map(len, reference)),
        "missing_lines": missing,
        "unexpected_lines": unexpected,
    }


def inspect_pdf(path, blocks):
    words, outside = [], 0
    with pymupdf.open(path) as pdf:
        for page in pdf:
            for block in page.get_text("dict", clip=pymupdf.INFINITE_RECT())["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        box = pymupdf.Rect(span["bbox"])
                        outside += int(not page.rect.contains(box))
                        if (
                            box.y0 < page.rect.height - 40
                        ):  # exclude the known running footer
                            words.append(span["text"])
        page_count = len(pdf)
    text = norm(" ".join(words))
    # Compare each JSON block with its own region of the review, including wrapped paragraphs.
    missing = []
    for i, block in enumerate(blocks):
        start = text.find(block["id"])
        end = (
            text.find(blocks[i + 1]["id"], start + 1)
            if i + 1 < len(blocks)
            else len(text)
        )
        excerpt = text[start:end] if start >= 0 else ""
        if norm("EN: " + block["text"]) not in excerpt:
            missing.append(block["id"] + "/source")
        if (
            not block["status"].startswith("preserved")
            and norm("ES: " + block["translated"]) not in excerpt
        ):
            missing.append(block["id"] + "/translation")
    return {
        "review_pages": page_count,
        "text_spans_outside_page": outside,
        "missing_pdf_fields": missing,
    }


def tokens(blocks, pattern):
    counts = Counter(source=0, retained=0, added=0)
    for b in blocks:
        if b["status"].startswith("preserved"):
            continue  # copied source is not a model prediction
        src, tgt = (Counter(pattern.findall(b[key])) for key in ("text", "translated"))
        counts.update(
            source=sum(src.values()),
            retained=sum((src & tgt).values()),
            added=sum((tgt - src).values()),
        )
    return dict(counts)


def record_alignment(blocks):
    total = matched = 0
    for block in blocks:
        source = block["text"].splitlines()
        target = (
            block["translated"].splitlines()
            if not block["status"].startswith("preserved")
            else []
        )
        total += len(source)
        matched += sum(
            bool(NUMBER.findall(a)) and NUMBER.findall(a) == NUMBER.findall(b)
            for a, b in zip(source, target)
        )
    return {"source_records": total, "matching_ids_in_position": matched}


def run_study(output):
    output.mkdir(parents=True, exist_ok=False)
    fixtures = Path(__file__).resolve().parents[1] / "examples/fixtures"
    if command := os.environ.get("TESSERACT_CMD"):
        pytesseract.pytesseract.tesseract_cmd = command
    proc = psutil.Process()
    peak = proc.memory_info().rss
    done = Event()

    def sample():
        nonlocal peak
        while not done.wait(0.05):
            peak = max(peak, proc.memory_info().rss)

    sampler = Thread(target=sample, daemon=True)
    sampler.start()
    try:
        torch.set_num_threads(2)
        t0 = time.perf_counter()
        provider = MarianTranslator(allow_download=False)
        study = {
            "engine": provider.name,
            "revision": provider.revision,
            "cached_model_load_seconds": round(time.perf_counter() - t0, 3),
            "platform": platform.system() + " " + platform.machine(),
            "python": platform.python_version(),
            "torch_threads": torch.get_num_threads(),
            "cpu": platform.processor() or platform.machine(),
            "tesseract": str(pytesseract.get_tesseract_version()).splitlines()[0],
            "packages": {
                k: version(k)
                for k in (
                    "torch",
                    "transformers",
                    "PyMuPDF",
                    "reportlab",
                    "pytesseract",
                    "psutil",
                )
            },
            "fixtures": {},
        }
        for name, reference in expected_pages().items():
            source, target = fixtures / (name + ".pdf"), output / name
            baseline = coverage(extract(source, "off"), reference)
            t0, cpu0 = time.perf_counter(), time.process_time()
            data = write_review(source, target, "images", None, lambda: provider)
            wall, cpu = time.perf_counter() - t0, time.process_time() - cpu0
            blocks = [b for p in data["pages"] for b in p["blocks"]]
            result = {
                "source_sha256": data["source_sha256"],
                "coverage": coverage(data, reference),
                "ocr_off_missing": len(baseline["missing_lines"]),
                "metrics": data["metrics"],
                "numbers": tokens(blocks, NUMBER),
                "units": tokens(blocks, UNIT),
                "flags": dict(Counter(flag for b in blocks for flag in b["flags"])),
                "pdf": inspect_pdf(target / "review.pdf", blocks),
                "original_identical": source.read_bytes()
                == (target / "original.pdf").read_bytes(),
                "wall_seconds": round(wall, 3),
                "process_cpu_seconds": round(cpu, 3),
                "review_pdf_bytes": (target / "review.pdf").stat().st_size,
            }
            if name == "long":
                result["record_alignment"] = record_alignment(blocks)
            study["fixtures"][name] = result
            print(name, result["metrics"], result["pdf"], flush=True)
        study["sampled_peak_parent_rss_mib"] = round(peak / 2**20, 1)
        (output / "study.json").write_text(
            json.dumps(study, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    finally:
        done.set()
        sampler.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    run_study(parser.parse_args().output_dir)
