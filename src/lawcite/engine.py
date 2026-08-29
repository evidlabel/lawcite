"""Core document-processing pipeline (API + PDF paths).

Extracted from the CLI so library callers and the ``lawcite`` command share
the same entry points without depending on treeparse wiring.
"""

import re

from .fetch.fetch_pdf import fetch_pdf_content
from .extract.extract_metadata import extract_metadata
from .save import save
from .parse.parse_general import parse_general_paragraphs
from .parse.parse_law import parse_law_paragraphs
from .api.client import (
    get_law,
    parse_identifier,
    eli_pdf_url,
    eli_url,
    RateLimitError,
)
from .parse.parse_api import (
    parse_law_structure,
    parse_selector,
    filter_by_selector,
    metadata_from_api,
    derive_namespace,
)

# Leading document-type line of a retsinformation PDF, e.g. "LBK nr 1150 af 03/11/2024".
_SHORT_NAME_RE = re.compile(r"^[A-ZÆØÅ]{2,5}\s+nr\s+\d", re.MULTILINE)


def _law_from_pdf(year: int, number: int, selector) -> tuple[dict, dict]:
    """Official-PDF fallback used when the structured API is rate-limited.

    Fetches ``…/eli/lta/{year}/{number}/pdf`` from retsinformation.dk (no API,
    no rate limit) and parses it with the legacy ``§``/``Stk.`` parser. Returns
    ``(paragraph_content, meta)`` shaped like the API path.
    """
    pdf = fetch_pdf_content(eli_pdf_url(year, number))
    _, document_date, document_author, document_title = extract_metadata(
        pdf, eli_url(year, number)
    )
    first_page = pdf.pages[0].extract_text() if pdf.pages else ""
    sn = _SHORT_NAME_RE.search(first_page)
    short_name = first_page[sn.start() :].splitlines()[0].strip() if sn else ""
    paragraph_content = filter_by_selector(parse_law_paragraphs(pdf), selector)
    meta = {
        "document_title": document_title,
        "document_author": document_author,
        "document_url": eli_url(year, number),
        "document_date": document_date,
        "short_name": short_name,
        "year": year,
        "number": number,
    }
    return paragraph_content, meta


def process_law(
    identifier: str,
    paragraphs: str = "",
    namespace: str = "",
    output_filename: str = "__temp.bib",
) -> None:
    """Fetch a law from the retsinformation API and save it as BibTeX/YAML/MD.

    Args:
        identifier: A law name (resolved via the API) or a ``year/number`` id.
        paragraphs: Optional narrow-lookup selector, e.g. ``"9"``, ``"9-12"``,
            ``"9,11,15a"``. Empty fetches the whole act.
        namespace: Optional Hayagriva key namespace override. Empty derives one
            from the law's short name (e.g. ``"lbk2024-1150"``).
        output_filename: Output file path; format chosen by extension.
    """
    selector = parse_selector(paragraphs)
    try:
        year, number = parse_identifier(identifier)
    except RateLimitError:
        raise ValueError(
            f"retsinformation-api.dk is rate-limited and '{identifier}' is not cached. "
            "Re-run with a 'year/number' identifier (e.g. 2024/1150) to use the "
            "official PDF fallback, or try again later."
        ) from None

    try:
        law_json = get_law(year, number)
        meta = metadata_from_api(law_json)
        paragraph_content = parse_law_structure(law_json, selector)
        print(f"Loaded law {year}/{number} from retsinformation API")
    except RateLimitError:
        print(
            f"retsinformation-api.dk rate-limited; falling back to official PDF "
            f"for {year}/{number}"
        )
        paragraph_content, meta = _law_from_pdf(year, number, selector)
        if not namespace and not meta["short_name"]:
            print(
                "Note: the PDF lacks a document-type line, so the key namespace "
                f"is '{year}-{number}' without the LBK/LOV prefix. Pass "
                "-n/--namespace for a stable key, or re-run when the API is up."
            )

    if not paragraph_content:
        raise ValueError(
            "No paragraphs extracted"
            + (f" for selector '{paragraphs}'" if paragraphs else "")
        )
    ns = namespace or derive_namespace(meta["short_name"], meta["year"], meta["number"])
    save(
        paragraph_content,
        meta["document_title"],
        meta["document_author"],
        meta["document_url"],
        meta["document_date"],
        output_filename,
        namespace=ns,
    )


def process_general_pdf(
    input_url: str,
    debug: bool = False,
    output_filename: str = "__temp.bib",
) -> None:
    """Process a general PDF from a URL and save as BibTeX, YAML, or Markdown."""
    pdf = fetch_pdf_content(input_url, debug)
    document_url, document_date, document_author, document_title = extract_metadata(
        pdf, input_url
    )
    paragraph_content = parse_general_paragraphs(pdf)
    if not paragraph_content:
        raise ValueError("No paragraphs extracted from the PDF")
    save(
        paragraph_content,
        document_title,
        document_author,
        document_url,
        document_date,
        output_filename,
    )
