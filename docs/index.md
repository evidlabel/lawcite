# lawcite docs

**lawcite** is a Python tool designed to convert Danish legal documents, such as those from retsinformation.dk, into BibTeX format for use in LaTeX documents. It processes PDFs with metadata (title, date, ministry) and paragraphs marked by `§`, generating clean BibTeX entries for legal citations.

## Getting Started

To learn how to install and use `lawcite`, see the [Usage](usage.md) page.
To learn how to use `lawcite` output, see the [Citing](output.md) page.

## Features

- Converts PDFs from dynamic API URLs (e.g., `retsinformation.dk/api/pdf/`) to BibTeX.
- Extracts metadata (title, date, ministry) from PDFs.
- Generates clean BibTeX keys (e.g., `konkurrencelovenp9stk2`).
- Supports debug mode to save fetched PDFs for inspection.




