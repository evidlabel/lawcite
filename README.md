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

# Specify output filename
lawcite pdf2bib --name konkurrenceloven.bib https://www.retsinformation.dk/api/pdf/217344

# Debug mode: Save fetched PDF for inspection
lawcite pdf2bib --debug https://www.retsinformation.dk/api/pdf/217344
```

The `pdf2bib` command processes PDFs with a structure similar to Danish legal documents (e.g., metadata on the first page, chapters, and paragraphs marked by `§`). 

It supports dynamic API URLs (e.g., `retsinformation.dk/api/pdf/`). BibTeX entries use the PDF's title as the `journal`, the ministry as the `author`, and clean keys (e.g., `foraldreansvarslovenp1stk1`). 

Use `--name` to specify the output BibTeX filename, or it defaults to a cleaned version of the document title. Use `--debug` to save the PDF for troubleshooting.

### Batch Processing

To process multiple laws listed in `examples/laws.yml` and save them as BibTeX files in the `examples` directory, run:
```bash
python examples/process_laws.py
```

This script reads the `laws.yml` file and generates `.bib` files (e.g., `examples/konkurrenceloven.bib`) for each law. If a `.bib` file already exists for a law, the script skips downloading and processing it to avoid overwriting existing files.

An example LaTeX document using these `.bib` files is provided in `examples/test.tex`, which demonstrates citing multiple Danish laws.

## Output

Example BibTeX output looks like this:
```bibtex
@article{konkurrenceloven10astk2,
 author = {Erhvervsministeriet},
 date = {2024-11-13},
 journal = {Bekendtgørelse af konkurrenceloven},
 publisher = {retsinformation.dk},
 title = {§10a Stk. 2. Påbud efter stk. 1 gælder i 2 år fra det tidspunkt, hvor afgørelsen er endelig.},
 url = {https://www.retsinformation.dk/api/pdf/244970}
}

@article{konkurrenceloven10astk3,
 author = {Erhvervsministeriet},
 date = {2024-11-13},
 journal = {Bekendtgørelse af konkurrencelaven},
 publisher = {retsinformation.dk},
 title = {§10a Stk. 3. Ved »samhandelsbetingelser« forstås det til enhver tid gældende grundlag, hvorefter en virksom- hed generelt fastsætter sine priser, rabatter, markedsføringstilskud og gratisydelser samt vilkårene for, at virksomheden vil kunne yde disse økonomiske fordele over for sine handelspartnere.},
 url = {https://www.retsinformation.dk/api/pdf/244970}
}
```

Which can be used in LaTeX documents as follows:
```latex
\cite{konkurrenceloven10astk2}
```

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

Documentation is automatically built and hosted on GitHub Pages via a GitHub Actions workflow. The hosted documentation is available at `https://<username>.github.io/lawcite/`.

## Disclaimer

`lawcite` is a tool for converting publicly available Danish laws into BibTeX format for use in LaTeX. 

It does not provide legal advice or interpret legal content. 

The tool processes and represents data from public sources, such as retsinformation.dk, without modification to the original content. 

Users are responsible for verifying the accuracy and applicability of the data for their purposes.
