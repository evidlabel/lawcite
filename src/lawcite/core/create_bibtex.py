import bibtexparser as bp
from typing import Dict, Tuple
import re
from unidecode import unidecode


def create_law_bibtex(
    paragraph_content: Dict[Tuple[str, str, str], str],
    document_title: str,
    document_author: str,
    document_url: str,
    document_date: str,
) -> bp.bibdatabase.BibDatabase:
    """Create BibTeX entries for a legal document."""
    bib_database = bp.bibdatabase.BibDatabase()

    title_lower = unidecode(document_title).lower()
    clean_title = re.sub(r"[^a-z0-9]+", "", title_lower)

    for chapter, paragraph, section in paragraph_content:
        # Clean chapter, paragraph and section for BibTeX ID
        clean_chapter = chapter.lower().replace(" ", "")
        clean_para = "p" + paragraph.lower().replace(" ", "")
        clean_section = section.lower().replace("stk. ", "stk").replace(".", "")

        short_title = f"§{paragraph} {section}"
        author = f"{document_title.capitalize()} {short_title},"
        title = paragraph_content[(chapter, paragraph, section)]

        entry = {
            "ENTRYTYPE": "article",
            "ID": f"{clean_title}{clean_para}{clean_section}",
            "author": author,
            "journal": document_author,
            "title": title,
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
    title_lower = unidecode(document_title).lower()
    clean_title = re.sub(r"[^a-z0-9]+", "", title_lower)

    for para_id, content in paragraph_content.items():
        author = f"{document_title.capitalize()} Paragraph {para_id},"
        entry = {
            "ENTRYTYPE": "article",
            "ID": f"{clean_title}_{para_id}",
            "author": author,
            "journal": document_author,
            "title": content,
            "url": document_url,
            "date": document_date,
        }
        bib_database.entries.append(entry)

    return bib_database
