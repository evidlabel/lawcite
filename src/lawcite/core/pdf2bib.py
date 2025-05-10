import requests
from pypdf import PdfReader
import bibtexparser as bp
from unidecode import unidecode
import re
import os
from typing import Dict, Tuple
from datetime import datetime


def fetch_pdf_content(input_url: str, debug: bool = False) -> PdfReader:
    """Fetch PDF content from a URL.

    Args:
        input_url: URL of the PDF file or PDF-generating API.
        debug: If True, save the fetched PDF to a file.

    Returns:
        PdfReader object containing the PDF content.

    Raises:
        requests.RequestException: If the request fails.
        ValueError: If the URL does not return a PDF.
    """
    response = requests.get(input_url, timeout=10)
    response.raise_for_status()

    if "application/pdf" not in response.headers.get("Content-Type", ""):
        raise ValueError("URL does not return a PDF file")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"temp_{timestamp}.pdf"
    with open(temp_filename, "wb") as f:
        f.write(response.content)

    pdf = PdfReader(temp_filename)
    print(f"Loaded PDF content from {input_url}")

    if debug:
        debug_filename = (
            f"debug_{unidecode(input_url.split('/')[-1] or 'document')}_{timestamp}.pdf"
        )
        os.rename(temp_filename, debug_filename)
        print(f"Saved PDF content to {debug_filename}")
    else:
        os.remove(temp_filename)

    return pdf


def extract_metadata(pdf: PdfReader, input_url: str) -> Tuple[str, str, str, str]:
    """Extract metadata from the PDF.

    Args:
        pdf: PdfReader object containing the PDF content.
        input_url: Original input URL for fallback.

    Returns:
        Tuple of (document_url, document_date, document_author, document_title).

    Raises:
        KeyError: If required metadata cannot be extracted.
    """
    first_page = pdf.pages[0].extract_text()
    lines = first_page.split("\n")

    document_url = input_url
    document_date = ""
    document_author = ""
    document_title = ""

    if "/Title" in pdf.metadata:
        document_title = pdf.metadata["/Title"]

    document_date = pdf.metadata.get("/CreationDate", "")

    if document_date:
        match = re.search(r"D:(\d{8})(\d{2})", document_date)
        if match:
            year, month, day = (
                match.group(1)[:4],
                match.group(1)[4:6],
                match.group(1)[6:],
            )
            document_date = f"{year}-{month}-{day}"
        else:
            document_date = datetime.now().strftime("%Y-%m-%d")
            print("Warning: No valid date found in PDF metadata, using current date.")
    else:
        document_date = datetime.now().strftime("%Y-%m-%d")
        print("Warning: No valid date found in PDF metadata, using current date.")

    for line in lines:
        line = line.strip()
        if "LBK nr" in line:
            match = re.search(r"LBK nr \d+ af (\d{2}/\d{2}/\d{4})", line)
            if match:
                day, month, year = match.group(1).split("/")
                document_date = f"{year}-{month}-{day}"
        elif line.startswith("Ministerium:"):
            document_author = (
                line.replace("Ministerium:", "").strip().split("Journal")[0].strip()
            )

    if not document_date:
        document_date = datetime.now().strftime("%Y-%m-%d")
        print("Warning: No valid date found in PDF, using current date.")
    if not document_author:
        document_author = "Unknown Ministry"
        print("Warning: No valid ministry found in PDF, using 'Unknown Ministry'.")
    if not document_title:
        raise KeyError("No valid title found in PDF")

    return document_url, document_date, document_author, document_title


def parse_paragraphs(pdf: PdfReader) -> Dict[Tuple[str, str], str]:
    """Parse paragraphs and subsections from the PDF.

    Args:
        pdf: PdfReader object containing the PDF content.

    Returns:
        Dictionary mapping (paragraph, section) tuples to content strings.
    """
    paragraph_content: Dict[Tuple[str, str], str] = {}
    current_paragraph = None
    current_section = None

    for page in pdf.pages:
        text = page.extract_text()
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect paragraph (e.g., "§ 1.", "§ 15a.", "§ 15 a.")
            para_match = re.match(r"§ (\d+\s*[a-zA-Z]?)\.\s*(.*)", line)
            if para_match:
                current_paragraph = para_match.group(1).replace(" ", "")
                current_section = "Stk. 1."
                content = para_match.group(2).strip()
                key = (current_paragraph, current_section)
                paragraph_content[key] = content if content else " "
                continue

            # Detect subsection (e.g., "Stk. 2.")
            stk_match = re.match(r"Stk\. (\d+)\.\s*(.*)", line)
            if stk_match and current_paragraph:
                current_section = f"Stk. {stk_match.group(1)}."
                content = stk_match.group(2).strip()
                key = (current_paragraph, current_section)
                paragraph_content[key] = content if content else " "
                continue

            # Append to current paragraph/section if applicable
            if current_paragraph and current_section:
                key = (current_paragraph, current_section)
                if key in paragraph_content:
                    paragraph_content[key] += " " + line

    return paragraph_content


def create_bibtex_entries(
    paragraph_content: Dict[Tuple[str, str], str],
    document_title: str,
    document_author: str,
    document_url: str,
    document_date: str,
) -> bp.bibdatabase.BibDatabase:
    """Create BibTeX entries from parsed content.

    Args:
        paragraph_content: Dictionary of parsed paragraph content.
        document_title: Title of the document.
        document_author: Author of the document (ministry).
        document_url: URL of the document.
        document_date: Date of the document.

    Returns:
        BibTeX database with entries.
    """
    bib_database = bp.bibdatabase.BibDatabase()

    # Clean title for use in BibTeX ID
    clean_title = (
        re.sub(r"[^a-zA-Z0-9]+", "", document_title).lower().split("elseaf")[-1]
    ).replace("_", "")

    for paragraph, section in paragraph_content:
        # Clean paragraph and section for BibTeX ID
        clean_para = paragraph.lower().replace("§", "p")
        clean_section = section.lower().replace("stk. ", "stk").replace(".", "")

        entry = {
            "ENTRYTYPE": "article",
            "ID": f"{clean_title}{clean_para}{clean_section}",
            "author": document_author,
            "publisher": "retsinformation.dk",
            "title": f"§{paragraph} {section} "
            + paragraph_content[(paragraph, section)].replace("\n\n", "\n"),
            "journal": document_title,
            "url": document_url,
            "date": document_date,
        }
        bib_database.entries.append(entry)

    return bib_database


def save_bibtex(
    bib_database: bp.bibdatabase.BibDatabase,
    document_title: str,
    output_filename: str | None = None,
    output_dir: str | None = None
) -> None:
    """Save BibTeX entries to a file.

    Args:
        bib_database: BibTeX database to save.
        document_title: Title of the document for generating the default output filename.
        output_filename: Optional specific filename for the BibTeX file.
        output_dir: Optional directory to save the BibTeX file; defaults to current directory.
    """
    if output_filename:
        filename = output_filename
    else:
        clean_title = (
            re.sub(r"[^a-zA-Z0-9]+", "", document_title).lower().split("elseaf")[-1]
        ).replace("_", "")
        filename = f"{clean_title}.bib"

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, filename)

    with open(filename, "w", encoding="utf-8") as bib_file:
        bp.dump(bib_database, bib_file)
        print(f"Written BibTeX output to {filename}")


def parse_pdf_to_bibtex(
    input_url: str,
    debug: bool = False,
    output_filename: str | None = None,
    output_dir: str | None = None
) -> None:
    """Convert PDF legal document from a URL to BibTeX format.

    Args:
        input_url: URL of the input PDF file or PDF-generating API.
        debug: If True, save fetched PDF to a file for debugging.
        output_filename: Optional specific filename for the BibTeX file.
        output_dir: Optional directory to save the BibTeX file; defaults to current directory.

    Raises:
        requests.RequestException: If the HTTP request fails.
        KeyError: If required metadata cannot be extracted.
        ValueError: If the URL does not return a PDF.
    """
    pdf = fetch_pdf_content(input_url, debug)
    document_url, document_date, document_author, document_title = extract_metadata(
        pdf, input_url
    )
    paragraph_content = parse_paragraphs(pdf)
    bib_database = create_bibtex_entries(
        paragraph_content, document_title, document_author, document_url, document_date
    )
    save_bibtex(bib_database, document_title, output_filename, output_dir)
