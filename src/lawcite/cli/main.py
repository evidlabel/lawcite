#!/usr/bin/env python
import argparse
from ..core.pdf2bib import parse_pdf_to_bibtex

def main() -> None:
    """Command-line interface for lawcite tools."""
    parser = argparse.ArgumentParser(
        description="lawcite: Tools for converting Danish legal documents to BibTeX"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand: pdf2bib
    parser_pdf2bib = subparsers.add_parser(
        "pdf2bib",
        description="Convert PDF legal documents from a URL to BibTeX format"
    )
    parser_pdf2bib.add_argument("input_url", help="URL of the input PDF file")
    parser_pdf2bib.add_argument(
        "--debug",
        action="store_true",
        help="Save fetched PDF content to a file for debugging"
    )

    args = parser.parse_args()

    if args.command == "pdf2bib":
        parse_pdf_to_bibtex(args.input_url, debug=args.debug)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
