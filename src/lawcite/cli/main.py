#!/usr/bin/env python
import argparse
from ..core.fetch_pdf import fetch_pdf_content
from ..core.extract_metadata import extract_metadata
from ..core.parse_law import parse_law_paragraphs
from ..core.parse_general import parse_general_paragraphs
from ..core.create_bibtex import create_law_bibtex, create_general_bibtex
from ..core.save_bibtex import save_bibtex

def process_law_pdf(input_url: str, debug: bool = False, output_filename: str | None = None) -> None:
    """Process a legal PDF to BibTeX format.

    Args:
        input_url: URL of the input PDF file.
        debug: If True, save fetched PDF for debugging.
        output_filename: Optional specific filename for the BibTeX file.
    """
    pdf = fetch_pdf_content(input_url, debug)
    document_url, document_date, document_author, document_title = extract_metadata(pdf, input_url)
    paragraph_content = parse_law_paragraphs(pdf)
    bib_database = create_law_bibtex(
        paragraph_content, document_title, document_author, document_url, document_date
    )
    save_bibtex(bib_database, document_title, output_filename)

def process_general_pdf(input_url: str, debug: bool = False, output_filename: str | None = None) -> None:
    """Process a general PDF to BibTeX format.

    Args:
        input_url: URL of the input PDF file.
        debug: If True, save fetched PDF for debugging.
        output_filename: Optional specific filename for the BibTeX file.
    """
    pdf = fetch_pdf_content(input_url, debug)
    document_url, document_date, document_author, document_title = extract_metadata(pdf, input_url)
    paragraph_content = parse_general_paragraphs(pdf)
    if not paragraph_content:
        raise ValueError("No paragraphs extracted from the PDF")
    bib_database = create_general_bibtex(
        paragraph_content, document_title, document_author, document_url, document_date
    )
    save_bibtex(bib_database, document_title, output_filename)

def main() -> None:
    """Command-line interface for lawcite tools."""
    parser = argparse.ArgumentParser(
        description="lawcite: Tools for converting documents to BibTeX"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand: law
    parser_law = subparsers.add_parser(
        "law",
        description="Convert legal PDF documents from a URL to BibTeX format"
    )
    parser_law.add_argument("input_url", help="URL of the input PDF file")
    parser_law.add_argument(
        "--debug",
        action="store_true",
        help="Save fetched PDF content to a file for debugging"
    )
    parser_law.add_argument(
        "--name",
        help="Specify the output BibTeX filename (e.g., konkurrenceloven.bib)"
    )

    # Subcommand: other
    parser_other = subparsers.add_parser(
        "other",
        description="Convert general PDF documents from a URL to BibTeX format"
    )
    parser_other.add_argument("input_url", help="URL of the input PDF file")
    parser_other.add_argument(
        "--debug",
        action="store_true",
        help="Save fetched PDF content to a file for debugging"
    )
    parser_other.add_argument(
        "--name",
        help="Specify the output BibTeX filename (e.g., document.bib)"
    )

    args = parser.parse_args()

    if args.command == "law":
        process_law_pdf(args.input_url, debug=args.debug, output_filename=args.name)
    elif args.command == "other":
        process_general_pdf(args.input_url, debug=args.debug, output_filename=args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
