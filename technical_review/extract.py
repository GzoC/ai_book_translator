import hashlib
import io
import os
from pathlib import Path

import pymupdf as fitz
import pytesseract
from PIL import Image

from .quality import validate_bbox


def ocr_region(page, rect):
    """OCR rasterized region; coordinates map back to PDF points, including mixed pages."""
    command = os.environ.get("TESSERACT_CMD")
    if command:
        pytesseract.pytesseract.tesseract_cmd = command
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect, alpha=False)
    image = Image.open(io.BytesIO(pix.tobytes("png")))
    try:
        data = pytesseract.image_to_data(
            image,
            lang="eng",
            config="--psm 6",
            output_type=pytesseract.Output.DICT,
            timeout=60,
        )
    except (
        pytesseract.TesseractNotFoundError,
        pytesseract.TesseractError,
        RuntimeError,
    ) as exc:
        raise RuntimeError(
            "OCR failed: install Tesseract with eng data, or select --ocr off explicitly"
        ) from exc
    groups = {}
    for i, text in enumerate(data["text"]):
        if not text.strip():
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        groups.setdefault(key, []).append(i)
    blocks = []
    sx = rect.width / image.width
    sy = rect.height / image.height
    for indices in groups.values():
        left = min(data["left"][i] for i in indices)
        top = min(data["top"][i] for i in indices)
        right = max(data["left"][i] + data["width"][i] for i in indices)
        bottom = max(data["top"][i] + data["height"][i] for i in indices)
        bbox = [
            rect.x0 + left * sx,
            rect.y0 + top * sy,
            rect.x0 + right * sx,
            rect.y0 + bottom * sy,
        ]
        blocks.append(
            {
                "text": " ".join(data["text"][i] for i in indices),
                "bbox": bbox,
                "origin": "ocr",
                "confidence": min(float(data["conf"][i]) for i in indices),
                "flags": ["ocr_review"],
            }
        )
    return blocks


def extract(path, ocr="off"):
    if ocr not in ("off", "images"):
        raise ValueError("Unknown OCR mode")
    path = Path(path)
    pages = []
    with fitz.open(path) as doc:
        if not doc.is_pdf or doc.needs_pass:
            raise ValueError("Only unencrypted PDFs are supported")
        if not 0 < len(doc) <= 50:
            raise ValueError("Scope: 1 to 50 pages per technical document")
        for page in doc:
            if page.rotation:
                raise ValueError(
                    "Rotated pages require a normalized source before extraction"
                )
            bounds = page.rect
            blocks = []
            warnings = []
            tables = [fitz.Rect(t.bbox) for t in page.find_tables().tables]
            for item in page.get_text("dict", sort=True)["blocks"]:
                if item["type"] != 0:
                    continue
                text = "\n".join(
                    "".join(span["text"] for span in line["spans"])
                    for line in item["lines"]
                ).strip()
                if not text:
                    continue
                box = fitz.Rect(item["bbox"])
                flags = []
                if any((box & t).get_area() > 0 for t in tables):
                    flags.append("table_preserved")
                if any(c in text for c in ("=", "∫", "∑", "√")):
                    flags.append("equation_preserved")
                blocks.append(
                    {
                        "text": text,
                        "bbox": list(box),
                        "origin": "digital",
                        "confidence": None,
                        "flags": flags,
                    }
                )
            regions = []
            for info in page.get_image_info():
                rect = fitz.Rect(info["bbox"]) & bounds
                if not rect.is_empty and not any(
                    (rect & r).get_area() / max(rect.get_area(), r.get_area()) > 0.95
                    for r in regions
                ):
                    regions.append(rect)
            # Blank/vector-only pages also get a full-page OCR attempt when explicitly requested.
            if not blocks and not regions:
                regions = [bounds]
            for rect in regions:
                if ocr == "off":
                    warnings.append(
                        {"code": "region_not_ocr_processed", "bbox": list(rect)}
                    )
                    continue
                found = ocr_region(page, rect)
                if not found:
                    warnings.append({"code": "ocr_no_text_found", "bbox": list(rect)})
                for block in found:
                    b = fitz.Rect(block["bbox"])
                    # Hidden text on scanned PDFs should not be counted twice.
                    duplicate = any(
                        (b & fitz.Rect(d["bbox"])).get_area() / max(b.get_area(), 0.001)
                        > 0.7
                        and block["text"].casefold() in d["text"].casefold()
                        for d in blocks
                    )
                    if not duplicate:
                        blocks.append(block)
            blocks.sort(key=lambda b: (round(b["bbox"][1], 1), b["bbox"][0]))
            for index, block in enumerate(blocks, 1):
                block["id"] = f"p{page.number + 1:03d}-b{index:03d}"
                block["bbox"] = validate_bbox(
                    block["bbox"], bounds.width, bounds.height
                )
            pages.append(
                {
                    "number": page.number + 1,
                    "width": bounds.width,
                    "height": bounds.height,
                    "blocks": blocks,
                    "warnings": warnings,
                }
            )
    return {
        "source_name": path.name,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "ocr_mode": ocr,
        "pages": pages,
    }
