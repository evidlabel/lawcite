#!/usr/bin/env python
from typing import Callable, Any

from treeparse import cli, command, argument, option

from lawcite.engine import process_law, process_general_pdf


def _law_callback(
    identifier: str,
    paragraphs: str = "",
    namespace: str = "",
    output_filename: str = "__temp.bib",
) -> None:
    process_law(identifier, paragraphs, namespace, output_filename)


def _other_callback(
    input_url: str,
    debug: bool = False,
    output_filename: str = "__temp.bib",
) -> None:
    process_general_pdf(input_url, debug, output_filename)


app = cli(
    name="lawcite",
    help="Tools for converting documents to BibTeX, YAML, or Markdown",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    # theme="monochrome",
)

law_cmd = command(
    name="law",
    help=(
        "Convert a Danish law (by name or year/number) from the retsinformation "
        "API to BibTeX, YAML, or Markdown, with optional narrow paragraph lookup"
    ),
    callback=_law_callback,
    arguments=[
        argument(
            name="identifier",
            arg_type=str,
            sort_key=0,
            help="Law name (e.g. konkurrenceloven) or year/number (e.g. 2024/1150)",
        ),
    ],
    options=[
        option(
            flags=["-p", "--paragraphs"],
            dest="paragraphs",
            arg_type=str,
            help="Narrow lookup: a § or range/list, e.g. 9, 9-12, or 9,11,15a",
            sort_key=0,
        ),
        option(
            flags=["-n", "--namespace"],
            dest="namespace",
            arg_type=str,
            help="Hayagriva key namespace override (default derived, e.g. lbk2024-1150)",
            sort_key=1,
        ),
        option(
            flags=["-f", "--file"],
            dest="output_filename",
            arg_type=str,
            help="Output file path (e.g. konkurrenceloven.yaml, default: __temp.bib)",
            sort_key=2,
        ),
    ],
)
app.commands.append(law_cmd)


def create_general_command(
    name: str,
    help_text: str,
    callback: Callable[[Any], None],
    file_example: str,
) -> command:
    """Create a PDF-based command (used for the general ``other`` command)."""
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


other_cmd = create_general_command(
    "other",
    "Convert general PDF documents from a URL to BibTeX, YAML, or Markdown format",
    _other_callback,
    "e.g., document.bib, document.yaml, or document.md",
)
app.commands.append(other_cmd)


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
