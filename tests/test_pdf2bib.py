import pytest
from unittest.mock import patch, Mock
from lawcite.cli.main import process_law, process_general_pdf
import io
import yaml


# --- Law fixtures: the structured retsinformation API JSON ------------------


@pytest.fixture
def mock_law_json():
    """A minimal slice of the GET /v1/lovgivning/{year}/{number} response."""

    def para(number, stks):
        return {
            "number": number,
            "stk": [{"number": n, "text": t, "litra": []} for n, t in stks],
        }

    return {
        "year": 2024,
        "number": 1150,
        "title": "Bekendtgørelse af konkurrenceloven",
        "popular_title": "Konkurrenceloven",
        "short_name": "LBK nr 1150 af 03/11/2024",
        "ministry": "Erhvervsministeriet",
        "ressort": None,
        "signature_date": "2024-11-03",
        "eli_uri": "/eli/lta/2024/1150",
        "structure": {
            "chapters": [
                {
                    "chapter_number": "Kapitel 1",
                    "chapter_title": "Formål",
                    "paragraph_groups": [
                        {
                            "paragraphs": [
                                para("§ 1.", [("Stk. 1.", "Loven har til formål...")]),
                                para(
                                    "§ 9.",
                                    [
                                        (
                                            "Stk. 1.",
                                            "Konkurrence- og Forbrugerstyrelsen kan efter anmeldelse...",
                                        ),
                                        (
                                            "Stk. 2.",
                                            "Konkurrence- og Forbrugerstyrelsen kan undlade at behandle en anmeldelse efter stk. 1...",
                                        ),
                                    ],
                                ),
                                para("§ 10.", [("Stk. 1.", "Forbuddet i § 6...")]),
                            ]
                        }
                    ],
                }
            ]
        },
    }


# --- General PDF fixtures (unchanged path) ----------------------------------


@pytest.fixture
def mock_pdf_content():
    return io.BytesIO(
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n2 0 obj\n<< /Type /Page >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    )


@pytest.fixture
def mock_law_pdf_reader():
    """A retsinformation law PDF, used to exercise the rate-limit PDF fallback."""

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
                "Kapitel 1\n"
                "Indledning\n"
            )
            page2 = MockPage()
            page2.text = (
                "§ 9. Konkurrence- og Forbrugerstyrelsen kan efter anmeldelse...\n"
                "Stk. 2. Konkurrence- og Forbrugerstyrelsen kan undlade...\n"
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


# --- Law tests (API-backed) -------------------------------------------------


def test_process_law_yaml(tmp_path, capsys, mock_law_json):
    output_file = tmp_path / "konkurrenceloven.yaml"

    with patch("lawcite.engine.get_law", return_value=mock_law_json):
        process_law("2024/1150", output_filename=str(output_file))

    captured = capsys.readouterr()
    assert "Loaded law 2024/1150 from retsinformation API" in captured.out
    assert f"Written Hayagriva YAML output to {output_file}" in captured.out

    with open(output_file, "r", encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)

    # Namespaced keys derived from the short name.
    assert "lbk2024-1150:main" in yaml_content
    assert yaml_content["lbk2024-1150:main"]["type"] == "Legislation"

    entry = yaml_content["lbk2024-1150:p9stk1"]
    assert entry["type"] == "Article"
    assert entry["author"] == ["Konkurrenceloven § 9 Stk. 1."]
    assert entry["publisher"] == "Erhvervsministeriet"
    assert "Konkurrence- og Forbrugerstyrelsen" in entry["title"]
    assert entry["url"] == "https://www.retsinformation.dk/eli/lta/2024/1150"
    assert entry["date"] == "2024-11-03"
    # Parent points at the act as Legislation.
    assert entry["parent"]["type"] == "Legislation"
    assert entry["parent"]["title"] == "Konkurrenceloven"


def test_process_law_yaml_narrow(tmp_path, mock_law_json):
    output_file = tmp_path / "kl9.yaml"

    with patch("lawcite.engine.get_law", return_value=mock_law_json):
        process_law("2024/1150", paragraphs="9", output_filename=str(output_file))

    with open(output_file, "r", encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)

    keys = set(yaml_content.keys())
    assert "lbk2024-1150:p9stk1" in keys
    assert "lbk2024-1150:p9stk2" in keys
    # § 1 and § 10 must be excluded by the narrow selector.
    assert "lbk2024-1150:p1stk1" not in keys
    assert "lbk2024-1150:p10stk1" not in keys


def test_process_law_namespace_override(tmp_path, mock_law_json):
    output_file = tmp_path / "kl.yaml"

    with patch("lawcite.engine.get_law", return_value=mock_law_json):
        process_law(
            "2024/1150", namespace="konkurrenceloven", output_filename=str(output_file)
        )

    with open(output_file, "r", encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)
    assert "konkurrenceloven:p9stk1" in yaml_content
    assert "konkurrenceloven:main" in yaml_content


def test_process_law_bib(tmp_path, capsys, mock_law_json):
    output_file = tmp_path / "konkurrenceloven.bib"

    with patch("lawcite.engine.get_law", return_value=mock_law_json):
        process_law("2024/1150", output_filename=str(output_file))

    captured = capsys.readouterr()
    assert f"Written BibTeX output to {output_file}" in captured.out

    with open(output_file, "r", encoding="utf-8") as f:
        bib_content = f.read()
    assert "@article{konkurrencelovenp9stk2" in bib_content
    assert "journal = {Erhvervsministeriet}" in bib_content
    assert "author = {Konkurrenceloven §9 Stk. 2.,}" in bib_content


def test_process_law_md(tmp_path, capsys, mock_law_json):
    output_file = tmp_path / "konkurrenceloven.md"

    with patch("lawcite.engine.get_law", return_value=mock_law_json):
        process_law("2024/1150", output_filename=str(output_file))

    captured = capsys.readouterr()
    assert f"Written Markdown output to {output_file}" in captured.out

    with open(output_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    assert "# Konkurrenceloven" in md_content
    assert "## Kapitel 1" in md_content
    assert "### § 9" in md_content
    assert "Stk. 1.:" in md_content
    assert "Stk. 2.:" in md_content


def test_process_law_pdf_fallback(tmp_path, capsys, mock_law_pdf_reader):
    """When the API is rate-limited, fall back to the official PDF."""
    from lawcite.api.client import RateLimitError

    output_file = tmp_path / "kl.yaml"
    with (
        patch("lawcite.engine.get_law", side_effect=RateLimitError("limited")),
        patch(
            "lawcite.engine.fetch_pdf_content", return_value=mock_law_pdf_reader
        ) as mock_fetch,
    ):
        process_law("2024/1150", output_filename=str(output_file))

    captured = capsys.readouterr()
    assert "falling back to official PDF" in captured.out
    # Hit the official eli-pdf URL, not the rate-limited API.
    assert mock_fetch.call_args[0][0] == (
        "https://www.retsinformation.dk/eli/lta/2024/1150/pdf"
    )

    with open(output_file, "r", encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)
    # Namespace still derived from the PDF's short-name line.
    assert "lbk2024-1150:main" in yaml_content
    assert "lbk2024-1150:p9stk2" in yaml_content
    assert yaml_content["lbk2024-1150:p9stk2"]["parent"]["type"] == "Legislation"


# --- General PDF tests (unchanged path) -------------------------------------


def test_process_general_yaml(
    tmp_path, capsys, mock_pdf_content, mock_general_pdf_reader
):
    input_url = "https://www.retsinformation.dk/api/pdf/233142"
    output_file = (
        tmp_path
        / "psykolognaevnetsvejledenderetningslinjerforautoriseredepsykologer.yaml"
    )

    with (
        patch("requests.get") as mock_get,
        patch("lawcite.fetch.fetch_pdf.PdfReader") as mock_reader,
    ):
        mock_response = Mock()
        mock_response.content = mock_pdf_content.read()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_reader.return_value = mock_general_pdf_reader

        process_general_pdf(input_url, output_filename=str(output_file))

    captured = capsys.readouterr()
    assert f"Written Hayagriva YAML output to {output_file}" in captured.out
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)
    assert isinstance(yaml_content, dict)
    entry = yaml_content[
        "psykolognaevnetsvejledenderetningslinjerforautoriseredepsykologer_para1"
    ]
    assert entry["type"] == "Article"
    assert "parent" not in entry  # general docs have no law parent
    assert entry["publisher"] == "Social- og Boligministeriet"
    assert "Disse retningslinjer" in entry["title"]
    assert entry["url"] == input_url
    assert entry["date"] == "2021-06-03"


def test_process_general_pdf(
    tmp_path, capsys, mock_pdf_content, mock_general_pdf_reader
):
    input_url = "https://www.retsinformation.dk/api/pdf/233142"
    output_file = (
        tmp_path
        / "psykolognaevnetsvejledenderetningslinjerforautoriseredepsykologer.bib"
    )

    with (
        patch("requests.get") as mock_get,
        patch("lawcite.fetch.fetch_pdf.PdfReader") as mock_reader,
    ):
        mock_response = Mock()
        mock_response.content = mock_pdf_content.read()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_reader.return_value = mock_general_pdf_reader

        process_general_pdf(input_url, output_filename=str(output_file))

    captured = capsys.readouterr()
    assert f"Written BibTeX output to {output_file}" in captured.out

    with open(output_file, "r", encoding="utf-8") as f:
        bib_content = f.read()
    assert (
        "@article{psykolognaevnetsvejledenderetningslinjerforautoriseredepsykologer_para1"
        in bib_content
    )
    assert "journal = {Social- og Boligministeriet}" in bib_content
