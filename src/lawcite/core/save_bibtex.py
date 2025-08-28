import bibtexparser as bp
import re
from unidecode import unidecode
import os


def save_bibtex(
    bib_database: bp.bibdatabase.BibDatabase,
    document_title: str,
    output_filename: str | None = None,
    output_dir: str | None = None,
) -> None:
    """Save BibTeX entries to a file.

    Args:
        bib_database: BibTeX database to save.
        document_title: Title of the document for generating the default output filename.
        output_filename: Optional specific filename for the BibTeX file.
        output_dir: Optional directory to save the BibTeX file; defaults to current directory.
    """
    if output_filename:
        filename = output_filename
    else:
        title_lower = unidecode(document_title).lower()
        prefix = "bekendtgorelse af "
        if title_lower.startswith(prefix):
            clean_title = title_lower[len(prefix) :]
        else:
            clean_title = title_lower
        clean_title = re.sub(r"[^a-z0-9]+", "", clean_title)
        filename = f"{clean_title}.bib"

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, filename)

    with open(filename, "w", encoding="utf-8") as bib_file:
        bp.dump(bib_database, bib_file)
        print(f"Written BibTeX output to {filename}")
