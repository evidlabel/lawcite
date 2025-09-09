import requests
from pypdf import PdfReader
from datetime import datetime
from unidecode import unidecode
import os


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
