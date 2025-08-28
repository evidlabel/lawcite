import bibtexparser as bp
from typing import Dict, Tuple
import re
from unidecode import unidecode


def create_law_bibtex(
    paragraph_content: Dict[Tuple[str, str], str],
    document_title: str,
    document_author: str,
    document_url: str,
    document_date: str,
) -> bp.bibdatabase.BibDatabase:
    """Create BibTeX entries for a legal document."""
    bib_database = bp.bibdatabase.BibDatabase()

    title_lower = unidecode(document_title).lower()
    prefix = "bekendtgorelse af "
    if title_lower.startswith(prefix):
        clean_title = title_lower[len(prefix) :]
    else:
        clean_title = title_lower
    clean_title = re.sub(r"[^a-z0-9]+", "", clean_title)

    for paragraph, section in paragraph_content:
        # Clean paragraph and section for BibTeX ID
        clean_para = "p" + paragraph.lower()
        clean_section = section.lower().replace("stk. ", "stk").replace(".", "")

        entry = {
            "ENTRYTYPE": "article",
            "ID": f"{clean_title}{clean_para}{clean_section}",
            "author": document_author,
            "publisher": "retsinformation.dk",
            "title": f"§{paragraph} {section} "
            + paragraph_content[(paragraph, section)].replace("\n\n", "\n"),
            "journal": document_title,
            "url": document_url,
            "date": document_date,
        }
        bib_database.entries.append(entry)

    return bib_database


def create_general_bibtex(
    paragraph_content: Dict[str, str],
    document_title: str,
    document_author: str,
    document_url: str,
    document_date: str,
) -> bp.bibdatabase.BibDatabase:
    """Create BibTeX entries for a general document."""
    bib_database = bp.bibdatabase.BibDatabase()

    # Clean title for use in BibTeX ID
    clean_title = (
        re.sub(r"[^a-z0-9]+", "", unidecode(document_title).lower())
    ).replace("_", "")

    for para_id, content in paragraph_content.items():
        entry = {
            "ENTRYTYPE": "article",
            "ID": f"{clean_title}_{para_id}",
            "author": document_author,
            "publisher": "retsinformation.dk",
            "title": content,
            "journal": document_title,
            "url": document_url,
            "date": document_date,
        }
        bib_database.entries.append(entry)

    return bib_database
