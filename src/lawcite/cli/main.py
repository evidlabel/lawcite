#!/usr/bin/env python
import rich_click as click
from ..core.fetch_pdf import fetch_pdf_content
from ..core.extract_metadata import extract_metadata
from ..core.parse_law import parse_law_paragraphs
from ..core.parse_general import parse_general_paragraphs
from ..core.create_bibtex import create_law_bibtex, create_general_bibtex
from ..core.save_bibtex import save_bibtex


def process_law_pdf(
    input_url: str,
    debug: bool = False,
    output_filename: str | None = None,
    output_dir: str | None = None,
) -> None:
    """Process a legal PDF to BibTeX format."""
    pdf = fetch_pdf_content(input_url, debug)
    document_url, document_date, document_author, document_title = extract_metadata(
        pdf, input_url
    )
    paragraph_content = parse_law_paragraphs(pdf)
    bib_database = create_law_bibtex(
        paragraph_content, document_title, document_author, document_url, document_date
    )
    save_bibtex(bib_database, document_title, output_filename, output_dir)


def process_general_pdf(
    input_url: str,
    debug: bool = False,
    output_filename: str | None = None,
    output_dir: str | None = None,
) -> None:
    """Process a general PDF to BibTeX format."""
    pdf = fetch_pdf_content(input_url, debug)
    document_url, document_date, document_author, document_title = extract_metadata(
        pdf, input_url
    )
    paragraph_content = parse_general_paragraphs(pdf)
    if not paragraph_content:
        raise ValueError("No paragraphs extracted from the PDF")
    bib_database = create_general_bibtex(
        paragraph_content, document_title, document_author, document_url, document_date
    )
    save_bibtex(bib_database, document_title, output_filename, output_dir)


@click.group(
    help="lawcite: Tools for converting documents to BibTeX",
    context_settings={"help_option_names": ["-h", "--help"]},
)
def main() -> None:
    pass


@main.command(help="Convert legal PDF documents from a URL to BibTeX format")
@click.argument("input_url")
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Save fetched PDF content to a file for debugging",
)
@click.option(
    "-f",
    "--file",
    help="Specify the output BibTeX filename (e.g., konkurrenceloven.bib)",
)
@click.option("-o", "--output-dir", help="Output directory for the BibTeX file")
def law(input_url: str, debug: bool, file: str | None, output_dir: str | None) -> None:
    process_law_pdf(input_url, debug=debug, output_filename=file, output_dir=output_dir)


@main.command(help="Convert general PDF documents from a URL to BibTeX format")
@click.argument("input_url")
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Save fetched PDF content to a file for debugging",
)
@click.option(
    "-f", "--file", help="Specify the output BibTeX filename (e.g., document.bib)"
)
@click.option("-o", "--output-dir", help="Output directory for the BibTeX file")
def other(
    input_url: str, debug: bool, file: str | None, output_dir: str | None
) -> None:
    process_general_pdf(
        input_url, debug=debug, output_filename=file, output_dir=output_dir
    )


if __name__ == "__main__":
    main()
