#!/usr/bin/env python
from ..core.fetch_pdf import fetch_pdf_content
from ..core.extract_metadata import extract_metadata
from ..core.parse_law import parse_law_paragraphs
from ..core.parse_general import parse_general_paragraphs
from ..core.create_bibtex import create_law_bibtex, create_general_bibtex
from ..core.save_bibtex import save_bibtex
from treeparse import cli, command, argument, option


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


app = cli(
    name="lawcite",
    help="Tools for converting documents to BibTeX",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    theme="monochrome",
)

law_cmd = command(
    name="law",
    help="Convert legal PDF documents from a URL to BibTeX format",
    callback=process_law_pdf,
    arguments=[
        argument(name="input_url", arg_type=str, sort_key=0),
    ],
    options=[
        option(
            flags=["-d", "--debug"],
            is_flag=True,
            help="Save fetched PDF content to a file for debugging",
            sort_key=0,
        ),
        option(
            flags=["-f", "--file"],
            help="Specify the output BibTeX filename (e.g., konkurrenceloven.bib)",
            arg_type=str,
            sort_key=1,
        ),
        option(
            flags=["-o", "--output-dir"],
            help="Output directory for the BibTeX file",
            arg_type=str,
            sort_key=2,
        ),
    ],
)
app.commands.append(law_cmd)

other_cmd = command(
    name="other",
    help="Convert general PDF documents from a URL to BibTeX format",
    callback=process_general_pdf,
    arguments=[
        argument(name="input_url", arg_type=str, sort_key=0),
    ],
    options=[
        option(
            flags=["-d", "--debug"],
            is_flag=True,
            help="Save fetched PDF content to a file for debugging",
            sort_key=0,
        ),
        option(
            flags=["-f", "--file"],
            help="Specify the output BibTeX filename (e.g., document.bib)",
            arg_type=str,
            sort_key=1,
        ),
        option(
            flags=["-o", "--output-dir"],
            help="Output directory for the BibTeX file",
            arg_type=str,
            sort_key=2,
        ),
    ],
)
app.commands.append(other_cmd)


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
