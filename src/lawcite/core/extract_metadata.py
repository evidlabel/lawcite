from pypdf import PdfReader
from datetime import datetime
import re


def extract_metadata(pdf: PdfReader, input_url: str) -> tuple[str, str, str, str]:
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

    # Prioritize text-based date (e.g., "VEJ nr 10267 af 03/06/2021")
    for line in lines:
        line = line.strip()
        if " af " in line and re.search(r"\d{2}/\d{2}/\d{4}", line):
            match = re.search(r"(\d{2}/\d{2}/\d{4})", line)
            if match:
                day, month, year = match.group(1).split("/")
                document_date = f"{year}-{month}-{day}"
        elif line.startswith("Ministerium:"):
            document_author = (
                line.replace("Ministerium:", "").strip().split("Journal")[0].strip()
            )

    # Fallback to metadata date if text-based date not found
    if not document_date:
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
                print(
                    "Warning: No valid date found in PDF metadata, using current date."
                )
        else:
            document_date = datetime.now().strftime("%Y-%m-%d")
            print("Warning: No date found, using current date.")

    if not document_author:
        document_author = "Unknown Author"
        print("Warning: No valid author found in PDF, using 'Unknown Author'.")
    if not document_title:
        document_title = "Untitled Document"
        print("Warning: No valid title found in PDF, using 'Untitled Document'.")

    return document_url, document_date, document_author, document_title
