# lawcite

Tools for converting PDF documents to BibTeX format for citing in LaTeX, with support for Danish laws and general documents.

## Installation

```bash
uv pip install . 
```

## Usage

### Converting Legal PDFs

Convert a Danish legal PDF to BibTeX:
```bash
lawcite law https://www.retsinformation.dk/api/pdf/244970
```

Specify output filename:
```bash
lawcite law --name konkurrenceloven.bib https://www.retsinformation.dk/api/pdf/244970
```

Debug mode to save the PDF:
```bash
lawcite law --debug https://www.retsinformation.dk/api/pdf/244970
```

The `law` command processes PDFs with a structure similar to Danish legal documents (e.g., metadata on the first page, chapters, and paragraphs marked by `§`). It supports dynamic API URLs (e.g., `retsinformation.dk/api/pdf/`). BibTeX entries use the PDF's title as the `journal`, the ministry as the `author`, and clean keys (e.g., `konkurrencelovenp1stk1`).

### Converting General PDFs

Convert a general PDF to BibTeX, with each paragraph cited individually:
```bash
lawcite other https://www.retsinformation.dk/api/pdf/233142
```

Specify output filename:
```bash
lawcite other --name psykologretningslinjer.bib https://www.retsinformation.dk/api/pdf/233142
```

Debug mode:
```bash
lawcite other --debug https://www.retsinformation.dk/api/pdf/233142
```

The `other` command processes any PDF, splitting content into paragraphs (separated by blank lines) and assigning incremental IDs (e.g., `para1`, `para2`). BibTeX entries use the PDF's title as the `journal`, the extracted author (or 'Unknown Author'), and keys like `psykolognvnetsvejledenderetningslinjer_para1`.

### Batch Processing

To process multiple laws listed in `examples/laws.yml` and save them as BibTeX files in the `examples` directory, run:
```bash
python examples/process_laws.py
```

This script reads the `laws.yml` file and generates `.bib` files (e.g., `examples/konkurrenceloven.bib`) for each law. If a `.bib` file already exists for a law, the script skips downloading and processing it to avoid overwriting existing files.

An example LaTeX document using these `.bib` files is provided in `examples/test.tex`, which demonstrates citing multiple Danish laws.

## Output

### Legal PDF Example
```bibtex
@article{konkurrencelovenp10astk2,
 author = {Erhvervsministeriet},
 date = {2024-11-13},
 journal = {Bekendtgørelse af konkurrenceloven},
 publisher = {retsinformation.dk},
 title = {§10a Stk. 2. Påbud efter stk. 1 gælder i 2 år fra det tidspunkt, hvor afgørelsen er endelig.},
 url = {https://www.retsinformation.dk/api/pdf/244970}
}
```

### General PDF Example
```bibtex
@article{psykolognvnetsvejledenderetningslinjerforautoriseredepsykologer_para1,
 author = {Social- og Boligministeriet},
 date = {2022-06-03},
 journal = {Psykolognævnets vejledende retningslinjer for autoriserede psykologer},
 publisher = {Unknown Publisher},
 title = {1. Indledning Disse retningslinjer fastsætter principper for autoriserede psykologers arbejde.},
 url = {https://www.retsinformation.dk/api/pdf/233142}
}
@article{psykolognvnetsvejledenderetningslinjerforautoriseredepsykologer_para2,
 author = {Social- og Boligministeriet},
 date = {2022-06-03},
 journal = {Psykolognævnets vejledende retningslinjer for autoriserede psykologer},
 publisher = {Unknown Publisher},
 title = {2. Etiske principper Psykologer skal handle i overensstemmelse med etiske standarder.},
 url = {https://www.retsinformation.dk/api/pdf/233142}
}
@article{psykolognvnetsvejledenderetningslinjerforautoriseredepsykologer_para3,
 author = {Social- og Boligministeriet},
 date = {2022-06-03},
 journal = {Psykolognævnets vejledende retningslinjer for autoriserede psykologer},
 publisher = {Unknown Publisher},
 title = {3. Fortrolighed Psykologer skal sikre fortrolighed for deres klienter.},
 url = {https://www.retsinformation.dk/api/pdf/233142}
}
```

Use in LaTeX documents as follows:
```latex
\cite{konkurrencelovenp10astk2}
\cite{psykolognvnetsvejledenderetningslinjerforautoriseredepsykologer_para1}
```

## Development

Run tests:
```bash
uv run pytest
```

Build and serve documentation:
```bash
uv run mkdocs serve
```

Documentation is automatically built and hosted on GitHub Pages via a GitHub Actions workflow. The hosted documentation is available at `https://evidlabel.github.io/lawcite/`.

## Disclaimer

`lawcite` is a tool for converting PDF documents into BibTeX format for use in LaTeX. 

It does not provide legal advice or interpret content. 

The tool processes and represents data from public sources, such as retsinformation.dk, without modification to the original content. 

Users are responsible for verifying the accuracy and applicability of the data for their purposes.
