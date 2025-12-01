import bibtexparser as bp
import re
from unidecode import unidecode
import os
import yaml
from typing import Dict
from .create_bibtex import create_law_bibtex, create_general_bibtex
from .save_md import save_markdown


def save_bibtex(
    paragraph_content: Dict,
    document_title: str,
    document_author: str,
    document_url: str,
    document_date: str,
    output_filename: str = "__temp.bib",
) -> None:
    """Save bibliography entries to a file in BibTeX, YAML, or Markdown format.

    Args:
        paragraph_content: Dictionary of paragraph content.
        document_title: Title of the document.
        document_author: Author of the document.
        document_url: URL of the document.
        document_date: Date of the document.
        output_filename: Output file path, determines format by extension.
    """
    # Generate law ID
    title_lower = unidecode(document_title).lower()
    clean_title = re.sub(r"[^a-z0-9]+", "", title_lower)
    law_id = clean_title

    if output_filename.endswith(('.yaml', '.yml')):
        # Save in Hayagriva YAML format
        entries = {}
        # Paragraph entries
        for key, content in paragraph_content.items():
            if isinstance(key, tuple) and len(key) == 3:  # Law: (chapter, paragraph, section)
                chapter, para, sec = key
                clean_chapter = chapter.lower().replace(" ", "")
                clean_para = "p" + para.lower().replace(" ", "")
                clean_sec = sec.lower().replace("stk. ", "stk").replace(".", "")
                para_id = f"{law_id}{clean_para}{clean_sec}"
                short_title = f"§{para} {sec}"
                author = [f"{document_title.capitalize()} {short_title}"]
            else:  # General: para_id
                para_id = f"{law_id}_{key}"
                author = [f"{document_title.capitalize()} Paragraph {key}"]
            entries[para_id] = {
                "type": "Article",
                "title": content,
                "author": author,
                "publisher": document_author,
                "url": document_url,
                "date": document_date,
            }
        # Ensure directory exists
        dir_path = os.path.dirname(output_filename)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(output_filename, "w", encoding="utf-8") as f:
            yaml.dump(entries, f, default_flow_style=False, allow_unicode=True)
        print(f"Written Hayagriva YAML output to {output_filename}")
    elif output_filename.endswith('.md'):
        # Save in Markdown format
        save_markdown(
            paragraph_content,
            document_title,
            document_author,
            document_url,
            document_date,
            law_id,
            output_filename,
        )
    else:
        # Save in BibTeX format
        if isinstance(paragraph_content, dict) and all(isinstance(k, tuple) and len(k) == 3 for k in paragraph_content):
            bib_database = create_law_bibtex(paragraph_content, document_title, document_author, document_url, document_date)
        else:
            bib_database = create_general_bibtex(paragraph_content, document_title, document_author, document_url, document_date)
        if not output_filename:
            filename = f"{clean_title}.bib"
        else:
            filename = output_filename
        dir_path = os.path.dirname(filename)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as bib_file:
            bp.dump(bib_database, bib_file)
        print(f"Written BibTeX output to {filename}")
