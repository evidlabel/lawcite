#!/usr/bin/env python
from typing import Callable, Dict, Any
from ..core.fetch_pdf import fetch_pdf_content
from ..core.extract_metadata import extract_metadata
from ..core.save_bibtex import save_bibtex
from ..core.parse_law import parse_law_paragraphs
from ..core.parse_general import parse_general_paragraphs
from treeparse import cli, command, argument, option


def process_pdf(
    input_url: str,
    debug: bool = False,
    output_filename: str = "__temp.bib",
    parser_func: Callable[[Any], Dict] = None,
) -> None:
    """Shared PDF processing logic."""
    pdf = fetch_pdf_content(input_url, debug)
    document_url, document_date, document_author, document_title = extract_metadata(
        pdf, input_url
    )
    paragraph_content = parser_func(pdf)
    if not paragraph_content:
        raise ValueError("No paragraphs extracted from the PDF")
    save_bibtex(
        paragraph_content,
        document_title,
        document_author,
        document_url,
        document_date,
        output_filename,
    )


def process_law_pdf(
    input_url: str,
    debug: bool = False,
    output_filename: str = "__temp.bib",
) -> None:
    """Process a legal PDF and save as BibTeX or YAML."""
    process_pdf(input_url, debug, output_filename, parse_law_paragraphs)


def process_general_pdf(
    input_url: str,
    debug: bool = False,
    output_filename: str = "__temp.bib",
) -> None:
    """Process a general PDF and save as BibTeX or YAML."""
    process_pdf(input_url, debug, output_filename, parse_general_paragraphs)


def create_command(
    name: str,
    help_text: str,
    parser_func: Callable[[Any], Dict],
    file_example: str,
) -> command:
    """Create a command with shared input structure."""

    def callback(
        input_url: str,
        debug: bool = False,
        output_filename: str = "__temp.bib",
    ):
        process_pdf(input_url, debug, output_filename, parser_func)

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
                arg_type=bool,
                help="Save fetched PDF content to a file for debugging",
                sort_key=0,
            ),
            option(
                flags=["-f", "--file"],
                dest="output_filename",
                help=f"Specify the output file path ({file_example}, default: __temp.bib)",
                arg_type=str,
                sort_key=1,
            ),
        ],
    )


app = cli(
    name="lawcite",
    help="Tools for converting documents to BibTeX, YAML, or Markdown",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    # theme="monochrome",
)

law_cmd = create_command(
    "law",
    "Convert legal PDF documents from a URL to BibTeX, YAML, or Markdown format",
    parse_law_paragraphs,
    "e.g., konkurrenceloven.bib, konkurrenceloven.yaml, or konkurrenceloven.md",
)
app.commands.append(law_cmd)

other_cmd = create_command(
    "other",
    "Convert general PDF documents from a URL to BibTeX, YAML, or Markdown format",
    parse_general_paragraphs,
    "e.g., document.bib, document.yaml, or document.md",
)
app.commands.append(other_cmd)


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
