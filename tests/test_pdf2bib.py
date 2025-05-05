import pytest
from unittest.mock import patch, Mock
from lawcite.core import pdf2bib
from PyPDF2 import PdfReader
import io

@pytest.fixture
def mock_pdf_content():
    return io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n2 0 obj\n<< /Type /Page >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF")

@pytest.fixture
def mock_pdf_reader():
    class MockPage:
        def extract_text(self):
            return self.text

    class MockPdfReader:
        def __init__(self):
            page1 = MockPage()
            page1.text = (
                "LBK nr 1768 af 30/11/2020\n"
                "Bekendtgørelse af forældreansvarsloven\n"
                "Ministerium: Social- og Boligministeriet\n"
            )
            page2 = MockPage()
            page2.text = (
                "§ 1. I alle forhold, som er omfattet af denne lov, skal hensynet til barnets bedste...\n"
                "Stk. 2. Barnet har ret til omsorg og tryghed...\n"
            )
            self.pages = [page1, page2]

    return MockPdfReader()

def test_pdf2bib_basic(tmp_path, capsys, mock_pdf_content, mock_pdf_reader):
    input_url = "https://www.retsinformation.dk/pdf/A20200176829.pdf"
    output_file = tmp_path / "bekendtgrelseafforaldreansvarsloven.bib"

    with patch("requests.get") as mock_get, patch("lawcite.core.pdf2bib.PdfReader") as mock_reader:
        mock_response = Mock()
        mock_response.content = mock_pdf_content.read()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_reader.return_value = mock_pdf_reader

        pdf2bib.parse_pdf_to_bibtex(input_url)

    captured = capsys.readouterr()
    assert f"Loaded PDF content from {input_url}" in captured.out
    assert f"Written BibTeX output to {output_file}" in captured.out
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        bib_content = f.read()
    assert "@article{foraldreansvarsloven_p1stk1" in bib_content
    assert "journal = {Bekendtgørelse af forældreansvarsloven}" in bib_content
    assert "author = {Social- og Boligministeriet}" in bib_content

def test_pdf2bib_dynamic_url(tmp_path, capsys, mock_pdf_content, mock_pdf_reader):
    input_url = "https://www.retsinformation.dk/api/pdf/217344"
    output_file = tmp_path / "bekendtgrelseafforaldreansvarsloven.bib"

    with patch("requests.get") as mock_get, patch("lawcite.core.pdf2bib.PdfReader") as mock_reader:
        mock_response = Mock()
        mock_response.content = mock_pdf_content.read()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_reader.return_value = mock_pdf_reader

        pdf2bib.parse_pdf_to_bibtex(input_url, debug=True)

    captured = capsys.readouterr()
    assert f"Loaded PDF content from {input_url}" in captured.out
    assert "Saved PDF content to debug_217344_" in captured.out
    assert f"Written BibTeX output to {output_file}" in captured.out
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        bib_content = f.read()
    assert "@article{foraldreansvarsloven_p1stk1" in bib_content
    assert "journal = {Bekendtgørelse af forældreansvarsloven}" in bib_content
    assert "author = {Social- og Boligministeriet}" in bib_content
