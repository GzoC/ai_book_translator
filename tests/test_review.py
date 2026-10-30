import hashlib
import shutil

import pymupdf as fitz
import pytest

from scripts.make_fixtures import create_fixtures
from technical_review.build import build_review
from technical_review.extract import extract
from technical_review.quality import check_translation, validate_bbox
from technical_review.translate import translate_document


@pytest.fixture(scope="session")
def fixtures(tmp_path_factory):
    return create_fixtures(tmp_path_factory.mktemp("pdfs"))


class TestProvider:
    name = "explicit-test-double"
    revision = "not-a-model"

    def translate(self, text):
        return "BORRADOR " + text


def test_digital_traceability(fixtures):
    data = extract(fixtures / "digital.pdf")
    assert (
        data["source_sha256"]
        == hashlib.sha256((fixtures / "digital.pdf").read_bytes()).hexdigest()
    )
    assert any("24 V" in b["text"] for b in data["pages"][0]["blocks"])
    assert len({b["id"] for b in data["pages"][0]["blocks"]}) == len(
        data["pages"][0]["blocks"]
    )


def test_mixed_flags_images_even_with_digital_text(fixtures):
    page = extract(fixtures / "mixed.pdf")["pages"][0]
    assert page["blocks"] and page["warnings"][0]["code"] == "region_not_ocr_processed"


def test_scanned_is_not_claimed_complete_without_ocr(fixtures):
    page = extract(fixtures / "scanned.pdf")["pages"][0]
    assert not page["blocks"] and page["warnings"]


def test_mixed_ocr_region_coordinates_with_explicit_double(fixtures, monkeypatch):
    import technical_review.extract as module

    seen = []

    def fake(page, rect):
        seen.append(tuple(rect))
        return [
            {
                "text": "Pressure sensor 10 bar",
                "bbox": list(rect),
                "origin": "ocr",
                "confidence": 90,
                "flags": ["ocr_review"],
            }
        ]

    monkeypatch.setattr(module, "ocr_region", fake)
    data = extract(fixtures / "mixed.pdf", ocr="images")
    assert seen and any(b["origin"] == "ocr" for b in data["pages"][0]["blocks"])
    assert any(b["origin"] == "digital" for b in data["pages"][0]["blocks"])


@pytest.mark.parametrize(
    "bbox",
    [
        [],
        [1, 2, 3],
        [2, 2, 1, 4],
        [0, 0, float("nan"), 4],
        [-1, 0, 2, 4],
        [0, 0, 700, 800],
    ],
)
def test_invalid_boxes_rejected(bbox):
    with pytest.raises(ValueError):
        validate_bbox(bbox, 612, 792)


def test_quality_checks_numbers_units_and_glossary():
    assert check_translation("Rated voltage: 24 V", "Tensión nominal: 24 V") == []
    assert "number_mismatch" in check_translation("24 V", "25 V")
    assert "unit_mismatch" in check_translation("24 V", "24 A")
    assert "glossary:circuit breaker" in check_translation(
        "circuit breaker", "circuito"
    )
    assert "empty_translation" in check_translation("test", "")


def test_tables_and_equations_preserved(fixtures):
    for name, flag in (
        ("table", "table_preserved"),
        ("equation", "equation_preserved"),
    ):
        data = translate_document(extract(fixtures / (name + ".pdf")), TestProvider())
        blocks = [b for p in data["pages"] for b in p["blocks"] if flag in b["flags"]]
        assert blocks and all(b["text"] == b["translated"] for b in blocks)


def test_provider_failure_preserves_original(fixtures):
    class Broken(TestProvider):
        def translate(self, text):
            raise RuntimeError("test failure")

    data = translate_document(extract(fixtures / "digital.pdf"), Broken())
    assert data["metrics"]["preserved_blocks"] == data["metrics"]["extracted_blocks"]
    assert data["metrics"]["translated_blocks"] == 0


def test_long_review_reflows_without_losing_end_marker(fixtures, tmp_path):
    data = extract(fixtures / "digital.pdf")
    block = data["pages"][0]["blocks"][0]
    block["translated"] = "Texto técnico. " * 1000 + " END_MARKER"
    block["status"] = "needs_review"
    for other in data["pages"][0]["blocks"][1:]:
        other["translated"] = other["text"]
        other["status"] = "draft"
    target = tmp_path / "review.pdf"
    result = build_review(data, target)
    with fitz.open(target) as pdf:
        text = "".join(p.get_text() for p in pdf)
        assert len(pdf) > 1 and "END_MARKER" in text
        assert result["source_overlay"] is False
        for page in pdf:
            for b in page.get_text("blocks"):
                assert (
                    b[0] >= 0
                    and b[1] >= 0
                    and b[2] <= page.rect.width + 1
                    and b[3] <= page.rect.height + 1
                )


def test_source_is_unchanged(fixtures, tmp_path):
    source = fixtures / "digital.pdf"
    before = source.read_bytes()
    data = translate_document(extract(source), TestProvider())
    build_review(data, tmp_path / "review.pdf")
    assert source.read_bytes() == before


@pytest.mark.ocr
@pytest.mark.skipif(
    shutil.which("tesseract") is None, reason="Real Tesseract executable unavailable"
)
def test_real_ocr_scanned_and_mixed(fixtures):
    for name in ("scanned", "mixed"):
        data = extract(fixtures / (name + ".pdf"), ocr="images")
        text = " ".join(b["text"] for p in data["pages"] for b in p["blocks"])
        assert "24 V" in text and "10 bar" in text
        assert any(b["origin"] == "ocr" for p in data["pages"] for b in p["blocks"])
