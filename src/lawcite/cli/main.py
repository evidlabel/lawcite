#!/usr/bin/env python
from typing import Callable, Dict, Any
from ..core.fetch_pdf import fetch_pdf_content
from ..core.extract_metadata import extract_metadata
from ..core.save_bibtex import save_bibtex
from ..core.parse_law import parse_law_paragraphs
from ..core.parse_general import parse_general_paragraphs
from ..core.create_bibtex import create_law_bibtex, create_general_bibtex
from treeparse import cli, command, argument, option


def process_pdf(
    input_url: str,
    debug: bool = False,
    output_filename: str = None,
    output_dir: str = None,
    parser_func: Callable[[Any], Dict] = None,
    creator_func: Callable[[Dict, str, str, str, str], Any] = None,
) -> None:
    """Shared PDF processing logic."""
    pdf = fetch_pdf_content(input_url, debug)
    document_url, document_date, document_author, document_title = extract_metadata(
        pdf, input_url
    )
    paragraph_content = parser_func(pdf)
    if not paragraph_content:
        raise ValueError("No paragraphs extracted from the PDF")
    bib_database = creator_func(
        paragraph_content, document_title, document_author, document_url, document_date
    )
    save_bibtex(bib_database, document_title, output_filename, output_dir)


def create_command(
    name: str,
    help_text: str,
    parser_func: Callable[[Any], Dict],
    creator_func: Callable[[Dict, str, str, str, str], Any],
    file_example: str,
) -> command:
    """Create a command with shared input structure."""

    def callback(
        input_url: str,
        debug: bool = False,
        output_filename: str = None,
        output_dir: str = None,
    ):
        process_pdf(
            input_url, debug, output_filename, output_dir, parser_func, creator_func
        )

    return command(
        name=name,
        help=help_text,
        callback=callback,
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
                dest="output_filename",
                help=f"Specify the output BibTeX filename ({file_example})",
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


app = cli(
    name="lawcite",
    help="Tools for converting documents to BibTeX",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    theme="monochrome",
)

law_cmd = create_command(
    "law",
    "Convert legal PDF documents from a URL to BibTeX format",
    parse_law_paragraphs,
    create_law_bibtex,
    "e.g., konkurrenceloven.bib",
)
app.commands.append(law_cmd)

other_cmd = create_command(
    "other",
    "Convert general PDF documents from a URL to BibTeX format",
    parse_general_paragraphs,
    create_general_bibtex,
    "e.g., document.bib",
)
app.commands.append(other_cmd)


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
