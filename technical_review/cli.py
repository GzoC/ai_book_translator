import argparse
import json
import shutil
import sys
import time
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

from .build import build_review
from .extract import extract
from .translate import MarianTranslator, translate_document


def read_glossary(path):
    glossary = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(glossary, dict) or not all(
        isinstance(term, str)
        and term.strip()
        and isinstance(target, str)
        and target.strip()
        for term, target in glossary.items()
    ):
        raise ValueError("Glossary must map nonempty strings to nonempty strings")
    return {key.strip(): value.strip() for key, value in glossary.items()}


def write_review(source, output, ocr, glossary, get_provider):
    if output.exists():
        raise FileExistsError("Output directory already exists; choose a new directory")
    if not source.is_file():
        raise FileNotFoundError(f"Input file not found: {source}")
    started = time.perf_counter()
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as tmp:
        staged = Path(tmp)
        original = staged / "original.pdf"
        shutil.copyfile(source, original)
        data = extract(original, ocr)
        data["source_name"] = source.name
        provider = get_provider()
        inference_start = time.perf_counter()
        translate_document(data, provider, glossary)
        data["metrics"]["translation_and_qa_seconds"] = round(
            time.perf_counter() - inference_start, 3
        )
        data["layout"] = build_review(data, staged / "review.pdf")
        data["metrics"]["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        (staged / "review.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        # Reserve the destination exclusively, even if another run finishes first.
        with ExitStack() as rollback:
            output.mkdir()
            rollback.callback(output.rmdir)
            for file in staged.iterdir():
                target = output / file.name
                file.rename(target)
                rollback.callback(target.unlink)
            rollback.pop_all()
    return data


def main(argv=None):
    p = argparse.ArgumentParser(
        description="English-Spanish technical PDF review, with original preserved"
    )
    p.add_argument("input", type=Path)
    p.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="New directory for the PDF pair and JSON",
    )
    p.add_argument("--ocr", choices=("off", "images"), default="off")
    p.add_argument(
        "--download-model",
        action="store_true",
        help="Allow download of pinned public weights",
    )
    p.add_argument(
        "--glossary",
        type=Path,
        help="JSON object replacing the default EN-to-ES review glossary",
    )
    args = p.parse_args(argv)
    try:
        glossary = read_glossary(args.glossary) if args.glossary else None
        data = write_review(
            args.input,
            args.output_dir,
            args.ocr,
            glossary,
            lambda: MarianTranslator(allow_download=args.download_model),
        )
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        print(f"technical-review: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(data["metrics"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
