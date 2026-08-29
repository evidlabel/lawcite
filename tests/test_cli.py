import pytest
from unittest.mock import patch

from lawcite.cli import main as cli
from lawcite.cli.main import (
    process_law,
    process_general_pdf,
    _law_callback,
    _other_callback,
    main,
)
from lawcite.api.client import RateLimitError


class _Page:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


class _Reader:
    def __init__(self, texts, metadata=None):
        self.pages = [_Page(t) for t in texts]
        self.metadata = metadata or {}


def test_process_law_rate_limited_resolve_message():
    with patch("lawcite.engine.parse_identifier", side_effect=RateLimitError("x")):
        with pytest.raises(ValueError, match="rate-limited"):
            process_law("konkurrenceloven", output_filename="/tmp/x.yaml")


def test_process_law_no_paragraphs(tmp_path):
    empty = {"year": 2024, "number": 1150, "structure": {"chapters": []}}
    with patch("lawcite.engine.get_law", return_value=empty):
        with pytest.raises(ValueError, match="No paragraphs extracted"):
            process_law("2024/1150", output_filename=str(tmp_path / "x.yaml"))


def test_process_law_fallback_note_when_no_short_name(tmp_path, capsys):
    # PDF without an "LBK nr …" header line -> namespace note is printed.
    reader = _Reader(
        [
            "Lov om ændring af noget\n",
            "§ 1. Første bestemmelse.\nStk. 2. Anden bestemmelse.\n",
        ],
        metadata={"/Title": "Lov om ændring", "/CreationDate": "D:20250101000000"},
    )
    with (
        patch("lawcite.engine.get_law", side_effect=RateLimitError("limited")),
        patch("lawcite.engine.fetch_pdf_content", return_value=reader),
    ):
        process_law("2025/716", output_filename=str(tmp_path / "x.yaml"))
    out = capsys.readouterr().out
    assert "falling back to official PDF" in out
    assert "without the LBK/LOV prefix" in out


def test_process_general_pdf_no_paragraphs(tmp_path):
    reader = _Reader(["Udskriftsdato: i dag\nMinisterium: X\n"], metadata={})
    with patch("lawcite.engine.fetch_pdf_content", return_value=reader):
        with pytest.raises(ValueError, match="No paragraphs"):
            process_general_pdf("http://x", output_filename=str(tmp_path / "x.bib"))


def test_callbacks_dispatch():
    with patch.object(cli, "process_law") as pl:
        _law_callback("2024/1150", "9", "ns", "out.yaml")
        pl.assert_called_once_with("2024/1150", "9", "ns", "out.yaml")
    with patch("lawcite.cli.main.process_general_pdf") as pg:
        _other_callback("http://x", True, "out.bib")
        pg.assert_called_once_with("http://x", True, "out.bib")


def test_main_runs_app():
    with patch.object(cli, "app") as app:
        main()
        app.run.assert_called_once()
