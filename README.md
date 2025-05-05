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
# Convert PDF from URL to BibTeX
lawcite pdf2bib https://www.retsinformation.dk/pdf/A20200176829.pdf

# Convert PDF from dynamic API URL to BibTeX
lawcite pdf2bib https://www.retsinformation.dk/api/pdf/217344

# Debug mode: Save fetched PDF for inspection
lawcite pdf2bib --debug https://www.retsinformation.dk/api/pdf/217344
```

Note: The `pdf2bib` command processes PDFs with a structure similar to Danish legal documents (e.g., metadata on the first page, chapters, and paragraphs marked by `§`). It supports both static `.pdf` URLs and dynamic API URLs (e.g., `retsinformation.dk/api/pdf/`). BibTeX entries use the PDF's title as the `journal`, the ministry as the `author`, and clean keys (e.g., `foraldreansvarsloven_pXstkY`). Use `--debug` to save the PDF for troubleshooting.

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
