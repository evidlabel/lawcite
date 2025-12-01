import pytest
from lawcite.core.save_md import save_markdown


def test_save_markdown_law(tmp_path):
    paragraph_content = {
        ("1", "9", "Stk. 1."): "Konkurrence- og Forbrugerstyrelsen kan efter anmeldelse fra en virksomhed eller sammenslutning af virksomheder erklære...",
        ("1", "9", "Stk. 2."): "Konkurrence- og Forbrugerstyrelsen kan undlade at behandle en anmeldelse efter stk. 1...",
    }
    document_title = "konkurrenceloven"
    document_author = "Erhvervsministeriet"
    document_url = "https://example.com"
    document_date = "2024-11-03"
    law_id = "konkurrenceloven"
    output_filename = tmp_path / "test.md"

    save_markdown(
        paragraph_content,
        document_title,
        document_author,
        document_url,
        document_date,
        law_id,
        str(output_filename),
    )

    assert output_filename.exists()
    with open(output_filename, "r", encoding="utf-8") as f:
        content = f.read()
    assert "# konkurrenceloven" in content
    assert "## Kapitel 1" in content
    assert "### § 9" in content
    assert "Stk. 1.: Konkurrence- og Forbrugerstyrelsen" in content
    assert "Stk. 2.: Konkurrence- og Forbrugerstyrelsen" in content


def test_save_markdown_general(tmp_path):
    paragraph_content = {
        "para1": "Disse retningslinjer fastsætter principper for autoriserede psykologers arbejde.",
        "para2": "Psykologer skal handle i overensstemmelse med etiske standarder.",
        "para3": "Psykologer skal sikre fortrolighed for deres klienter.",
    }
    document_title = "Psykolognævnets vejledende retningslinjer for autoriserede psykologer"
    document_author = "Social- og Boligministeriet"
    document_url = "https://example.com"
    document_date = "2021-06-03"
    law_id = "psykolognaevnetsvejledenderetningslinjerforautoriseredepsykologer"
    output_filename = tmp_path / "test.md"

    save_markdown(
        paragraph_content,
        document_title,
        document_author,
        document_url,
        document_date,
        law_id,
        str(output_filename),
    )

    assert output_filename.exists()
    with open(output_filename, "r", encoding="utf-8") as f:
        content = f.read()
    assert "# Psykolognævnets vejledende retningslinjer for autoriserede psykologer" in content
    assert "### Paragraph 1" in content
    assert "### Paragraph 2" in content
    assert "### Paragraph 3" in content
    assert "Disse retningslinjer" in content
    assert "Psykologer skal handle" in content
    assert "Psykologer skal sikre" in content
