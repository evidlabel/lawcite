import os

import pytest
from unittest.mock import Mock, patch

from lawcite.extract.extract_metadata import extract_metadata
from lawcite.fetch.fetch_pdf import fetch_pdf_content
from lawcite.parse.parse_general import parse_general_paragraphs


class _Page:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


class _Reader:
    def __init__(self, texts, metadata=None):
        self.pages = [_Page(t) for t in texts]
        self.metadata = metadata or {}


# --- extract_metadata -------------------------------------------------------


def test_extract_metadata_creationdate_and_fallbacks():
    pdf = _Reader(
        ["Heading line\nno date and no ministry here\n"],
        metadata={"/CreationDate": "D:20230115000000"},
    )
    url, date, author, title = extract_metadata(pdf, "http://x/y")
    assert date == "2023-01-15"  # parsed from /CreationDate
    assert author == "Unknown Author"  # no Ministerium line
    assert title == "Untitled Document"  # no /Title
    assert url == "http://x/y"


def test_extract_metadata_no_date_uses_today():
    pdf = _Reader(["Just a heading\n"], metadata={})
    _, date, _, _ = extract_metadata(pdf, "http://x")
    assert len(date) == 10 and date.count("-") == 2  # YYYY-MM-DD (today)


def test_extract_metadata_malformed_creationdate_uses_today():
    pdf = _Reader(["Heading\n"], metadata={"/CreationDate": "not-a-date"})
    _, date, _, _ = extract_metadata(pdf, "http://x")
    assert len(date) == 10  # falls back to today's date


# --- fetch_pdf --------------------------------------------------------------


def test_fetch_pdf_rejects_non_pdf():
    resp = Mock()
    resp.headers = {"Content-Type": "text/html"}
    resp.raise_for_status = Mock()
    resp.content = b"<html></html>"
    with patch("requests.get", return_value=resp):
        with pytest.raises(ValueError, match="does not return a PDF"):
            fetch_pdf_content("http://x/notpdf")


def test_fetch_pdf_debug_saves_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    resp = Mock()
    resp.headers = {"Content-Type": "application/pdf"}
    resp.raise_for_status = Mock()
    resp.content = b"%PDF-1.4 fake"
    sentinel = object()
    with (
        patch("requests.get", return_value=resp),
        patch("lawcite.fetch.fetch_pdf.PdfReader", return_value=sentinel),
    ):
        out = fetch_pdf_content("http://x/doc123", debug=True)
    assert out is sentinel
    debug_files = [f for f in os.listdir(tmp_path) if f.startswith("debug_")]
    assert debug_files, "debug PDF should have been written"
    assert "Saved PDF content to" in capsys.readouterr().out


# --- parse_general edge cases ----------------------------------------------


def test_parse_general_numbered_next_line_and_final_flush():
    pdf = _Reader(["Body sentence one.\n2. Section two\n"], metadata={})
    out = parse_general_paragraphs(pdf)
    assert out["para1"] == "Body sentence one."
    assert out["para2"] == "2. Section two"  # captured by the final flush


def test_parse_general_empty_warns(capsys):
    # All lines are skipped page-1 header lines -> nothing extracted.
    pdf = _Reader(["Udskriftsdato: i dag\nMinisterium: X\n"], metadata={})
    out = parse_general_paragraphs(pdf)
    assert out == {}
    assert "No paragraphs extracted" in capsys.readouterr().out


def test_parse_general_trailing_no_period_final_flush():
    # No trailing blank line -> exercises the non-numbered split + final flush.
    pdf = _Reader(["First sentence here.\nTrailing words no period"], metadata={})
    out = parse_general_paragraphs(pdf)
    assert out["para1"] == "First sentence here."
    assert out["para2"] == "Trailing words no period"


def test_parse_general_skips_empty_page():
    # A later page whose extract_text() is falsy is skipped (continue branch).
    pdf = _Reader(["Real body text here.", ""], metadata={})
    out = parse_general_paragraphs(pdf)
    assert any("Real body text" in v for v in out.values())


def test_parse_law_continuation_line():
    from lawcite.parse.parse_law import parse_law_paragraphs

    pdf = _Reader(
        ["§ 1. First part of the rule\nwhich continues here.\nStk. 2. Second.\n"],
        metadata={},
    )
    out = parse_law_paragraphs(pdf)
    assert out[("1", "1", "Stk. 1.")] == "First part of the rule which continues here."
    assert out[("1", "1", "Stk. 2.")] == "Second."


def test_save_bibtex_default_filename(tmp_path, monkeypatch):
    from lawcite.save.save_bibtex import save_bibtex

    monkeypatch.chdir(tmp_path)
    save_bibtex(
        {"para1": "Some text."},
        "Mytitle",
        "Author",
        "http://x",
        "2024-01-01",
        output_filename="",
    )
    assert (tmp_path / "mytitle.bib").exists()
