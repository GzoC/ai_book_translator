import json

import pytest

from scripts.make_fixtures import create_fixtures
from technical_review import cli


@pytest.fixture(scope="module")
def source(tmp_path_factory):
    return create_fixtures(tmp_path_factory.mktemp("inputs")) / "digital.pdf"


def test_bad_glossary_fails_before_model_or_output(source, tmp_path, capsys):
    target = tmp_path / "out"
    glossary = tmp_path / "terms.json"
    for content in ("{", "null", '["sensor"]', '{"sensor": "  "}'):
        glossary.write_text(content, encoding="utf-8")
        assert (
            cli.main(
                [str(source), "--output-dir", str(target), "--glossary", str(glossary)]
            )
            == 2
        )
        assert "technical-review:" in capsys.readouterr().err
        assert not target.exists()


def test_existing_destination_is_preserved(source, tmp_path):
    sentinel = tmp_path / "original.pdf"
    sentinel.write_bytes(b"existing file")
    assert cli.main([str(source), "--output-dir", str(tmp_path)]) == 2
    assert sentinel.read_bytes() == b"existing file"


def test_missing_input_and_failed_build_leave_destination_available(
    source, tmp_path, monkeypatch
):
    target = tmp_path / "out"
    assert cli.main([str(tmp_path / "missing.pdf"), "--output-dir", str(target)]) == 2
    assert not target.exists()

    class TranslationDouble:
        name, revision = "test-double", "test"

        def translate(self, text):
            return text

    monkeypatch.setattr(cli, "MarianTranslator", lambda **kw: TranslationDouble())

    def fail(*args):
        raise RuntimeError("injected renderer failure")

    with monkeypatch.context() as patch:
        patch.setattr(cli, "build_review", fail)
        assert cli.main([str(source), "--output-dir", str(target)]) == 2
    assert not target.exists()

    glossary = tmp_path / "terms.json"
    glossary.write_text('{"power supply":"fuente"}', encoding="utf-8")
    assert (
        cli.main(
            [str(source), "--output-dir", str(target), "--glossary", str(glossary)]
        )
        == 0
    )
    report = json.loads((target / "review.json").read_text(encoding="utf-8"))
    first = report["pages"][0]["blocks"][0]
    assert "glossary:power supply" in first["flags"]
    assert (target / "original.pdf").read_bytes() == source.read_bytes()
