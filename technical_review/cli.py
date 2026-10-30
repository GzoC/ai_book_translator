import argparse
import json
import shutil
import time
from pathlib import Path

from .build import build_review
from .extract import extract
from .translate import MarianTranslator, translate_document


def main():
    p = argparse.ArgumentParser(
        description="English-Spanish technical PDF review, with original preserved"
    )
    p.add_argument("input", type=Path)
    p.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="New directory; existing paths are preserved",
    )
    p.add_argument("--ocr", choices=("off", "images"), default="off")
    p.add_argument(
        "--download-model",
        action="store_true",
        help="Allow download of pinned public model; documents remain local",
    )
    p.add_argument(
        "--glossary",
        type=Path,
        help="JSON map of English terms to expected Spanish terms for QA",
    )
    args = p.parse_args()
    if args.output_dir.exists():
        p.error("Output directory already exists; choose a new directory")
    started = time.perf_counter()
    data = extract(args.input, args.ocr)
    glossary = (
        json.loads(args.glossary.read_text(encoding="utf-8")) if args.glossary else None
    )
    if glossary is not None and (
        not isinstance(glossary, dict)
        or not all(
            isinstance(k, str) and k and isinstance(v, str) and v
            for k, v in glossary.items()
        )
    ):
        p.error("Glossary must map nonempty strings to nonempty strings")
    provider = MarianTranslator(allow_download=args.download_model)
    data = translate_document(data, provider, glossary)
    args.output_dir.mkdir(parents=True)
    shutil.copy2(args.input, args.output_dir / "original.pdf")
    data["layout"] = build_review(data, args.output_dir / "review.pdf")
    data["metrics"]["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    (args.output_dir / "review.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(data["metrics"], ensure_ascii=False))


if __name__ == "__main__":
    main()
