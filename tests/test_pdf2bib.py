import pytest
from unittest.mock import patch, Mock
from lawcite.cli.main import process_law_pdf, process_general_pdf
import io

@pytest.fixture
def mock_pdf_content():
    return io.BytesIO(
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n2 0 obj\n<< /Type /Page >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    )

@pytest.fixture
def mock_law_pdf_reader():
    class MockPage:
        def extract_text(self):
            return self.text

    class MockPdfReader:
        def __init__(self):
            page1 = MockPage()
            page1.text = (
                "LBK nr 1150 af 03/11/2024\n"
                "Bekendtgørelse af konkurrenceloven\n"
                "Ministerium: Erhvervsministeriet\n"
            )
            page2 = MockPage()
            page2.text = (
                "§ 9. Konkurrence- og Forbrugerstyrelsen kan efter anmeldelse fra en virksomhed eller sammenslutning af virksomheder erklære...\n"
                "Stk. 2. Konkurrence- og Forbrugerstyrelsen kan undlade at behandle en anmeldelse efter stk. 1...\n"
            )
            self.pages = [page1, page2]
            self.metadata = {
                "/Title": "Bekendtgørelse af konkurrenceloven",
                "/CreationDate": "D:20241103000000",
            }

    return MockPdfReader()

@pytest.fixture
def mock_general_pdf_reader():
    class MockPage:
        def extract_text(self):
            return self.text

    class MockPdfReader:
        def __init__(self):
            page1 = MockPage()
            page1.text = (
                "Udskriftsdato: 17. maj 2025\n"
                "VEJ nr 10267 af 03/06/2021 (Gældende)\n"
                "Psykolognævnets vejledende retningslinjer for autoriserede psykologer\n"
                "Ministerium: Social- og Boligministeriet\n"
                "\n"
                "1. Indledning\n"
                "Disse retningslinjer fastsætter principper for autoriserede psykologers arbejde.\n"
                "\n"
                "2. Etiske principper\n"
                "Psykologer skal handle i overensstemmelse med etiske standarder.\n"
                "\n"
                "3. Fortrolighed\n"
                "Psykologer skal sikre fortrolighed for deres klienter.\n"
            )
            self.pages = [page1]
            self.metadata = {
                "/Title": "Psykolognævnets vejledende retningslinjer for autoriserede psykologer",
                "/CreationDate": "D:20220603000000",
            }

    return MockPdfReader()

def test_process_law_pdf(tmp_path, capsys, mock_pdf_content, mock_law_pdf_reader):
    input_url = "https://www.retsinformation.dk/api/pdf/244970"
    output_file = tmp_path / "konkurrenceloven.bib"

    with (
        patch("requests.get") as mock_get,
        patch("lawcite.core.fetch_pdf.PdfReader") as mock_reader,
    ):
        mock_response = Mock()
        mock_response.content = mock_pdf_content.read()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_reader.return_value = mock_law_pdf_reader

        process_law_pdf(input_url, output_dir=str(tmp_path))

    captured = capsys.readouterr()
    assert f"Loaded PDF content from {input_url}" in captured.out
    assert f"Written BibTeX output to {output_file}" in captured.out
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        bib_content = f.read()
    assert "@article{konkurrencelovenp9stk2" in bib_content
    assert "journal = {Bekendtgørelse af konkurrenceloven}" in bib_content
    assert "author = {Erhvervsministeriet}" in bib_content

def test_process_general_pdf(tmp_path, capsys, mock_pdf_content, mock_general_pdf_reader):
    input_url = "https://www.retsinformation.dk/api/pdf/233142"
    output_file = tmp_path / "psykolognaevnetsvejledenderetningslinjerforautoriseredepsykologer.bib"

    with (
        patch("requests.get") as mock_get,
        patch("lawcite.core.fetch_pdf.PdfReader") as mock_reader,
    ):
        mock_response = Mock()
        mock_response.content = mock_pdf_content.read()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_reader.return_value = mock_general_pdf_reader

        process_general_pdf(input_url, output_dir=str(tmp_path))

    captured = capsys.readouterr()
    assert f"Loaded PDF content from {input_url}" in captured.out
    assert f"Written BibTeX output to {output_file}" in captured.out
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        bib_content = f.read()
    assert "@article{psykolognaevnetsvejledenderetningslinjerforautoriseredepsykologer_para1" in bib_content
    assert "@article{psykolognaevnetsvejledenderetningslinjerforautoriseredepsykologer_para2" in bib_content
    assert "@article{psykolognaevnetsvejledenderetningslinjerforautoriseredepsykologer_para3" in bib_content
    assert "journal = {Psykolognævnets vejledende retningslinjer for autoriserede psykologer}" in bib_content
    assert "author = {Social- og Boligministeriet}" in bib_content
