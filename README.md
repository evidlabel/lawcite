# lawcite

Tools for working with Danish laws in LaTeX, converting PDF legal documents to BibTeX format.

## Installation

```bash
poetry install
poetry shell
```

Activate the virtual environment with `poetry shell` to use the `lawcite` command.

## Usage

```bash
# Convert PDF from a URL to BibTeX
lawcite pdf2bib https://www.retsinformation.dk/api/pdf/217344

# Debug mode: Save fetched PDF for inspection
lawcite pdf2bib --debug https://www.retsinformation.dk/api/pdf/217344
```

The `pdf2bib` command processes PDFs with a structure similar to Danish legal documents (e.g., metadata on the first page, chapters, and paragraphs marked by `§`). It supports dynamic API URLs (e.g., `retsinformation.dk/api/pdf/`). BibTeX entries use the PDF's title as the `journal`, the ministry as the `author`, and clean keys (e.g., `foraldreansvarslovenp1stk1`). Use `--debug` to save the PDF for troubleshooting.

## Development

Run tests:
```bash
poetry run pytest
```

Format code:
```bash
poetry run black .
```

Build and serve documentation:
```bash
poetry run mkdocs serve
```

## Disclaimer

`lawcite` is a tool for converting publicly available Danish legal documents into BibTeX format for use in LaTeX. It does not provide legal advice or interpret legal content. The tool processes and represents data from public sources, such as retsinformation.dk, without modification to the original content. Users are responsible for verifying the accuracy and applicability of the data for their purposes.