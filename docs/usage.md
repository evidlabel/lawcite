# Usage

This section describes how to use the lawcite command-line tools. Ensure you have activated the Poetry virtual environment with `poetry shell` before running commands.

## PDF to BibTeX

Convert a PDF from a URL to BibTeX format:
```bash
lawcite pdf2bib https://www.retsinformation.dk/pdf/A20200176829.pdf
```

Convert a PDF from a dynamic API URL:
```bash
lawcite pdf2bib https://www.retsinformation.dk/api/pdf/217344
```

Expects PDFs with metadata (title, date, ministry) on the first page and paragraphs marked by `§`. Supports both static `.pdf` URLs and dynamic API URLs. BibTeX entries use the PDF's title as the `journal`, the ministry as the `author`, and clean keys (e.g., `foraldreansvarsloven_pXstkY`). Use `--debug` to save the PDF for troubleshooting:
```bash
lawcite pdf2bib --debug https://www.retsinformation.dk/api/pdf/217344
```

## LaTeX to HTML

This functionality has been deprecated.
