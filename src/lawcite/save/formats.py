"""Output format adapters: BibTeX, Hayagriva YAML, Markdown.

Each format knows how to serialize law vs general paragraph maps and write
them to a path. The thin ``save()`` dispatcher picks a format by extension.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping, Protocol

import bibtexparser as bp
import yaml

from .. import __version__
from ..create.create_bibtex import create_general_bibtex, create_law_bibtex
from .common import ensure_parent_dir, is_law_content


class OutputFormat(Protocol):
    """Serialize paragraph content to a file."""

    def write(
        self,
        paragraph_content: Mapping[Any, str],
        *,
        document_title: str,
        document_author: str,
        document_url: str,
        document_date: str,
        output_path: str,
        law_id: str,
        namespace: str | None = None,
    ) -> None: ...


def _watermark(url: str | None = None) -> str:
    """Provenance comment stamped above every Hayagriva entry lawcite writes.

    Format: ``# generated-by: lawcite v<version> · <date> · <source-url>``.
    The comment is inert YAML; downstream tools ignore it but a reader can see
    which tool produced the entry and from where.
    """
    wm = f"# generated-by: lawcite v{__version__} · {date.today().isoformat()}"
    if url:
        wm += f" · {url}"
    return wm + "\n"


class BibTeXFormat:
    """Write a BibTeX database (``.bib``)."""

    def write(
        self,
        paragraph_content: Mapping[Any, str],
        *,
        document_title: str,
        document_author: str,
        document_url: str,
        document_date: str,
        output_path: str,
        law_id: str,
        namespace: str | None = None,
    ) -> None:
        del law_id, namespace  # BibTeX keys are derived inside create_* helpers
        if is_law_content(paragraph_content):
            bib_database = create_law_bibtex(
                paragraph_content,
                document_title,
                document_author,
                document_url,
                document_date,
            )
        else:
            bib_database = create_general_bibtex(
                paragraph_content,
                document_title,
                document_author,
                document_url,
                document_date,
            )
        ensure_parent_dir(output_path)
        with open(output_path, "w", encoding="utf-8") as bib_file:
            bp.dump(bib_database, bib_file)
        print(f"Written BibTeX output to {output_path}")


class HayagrivaFormat:
    """Write Hayagriva YAML (``.yaml`` / ``.yml``)."""

    def write(
        self,
        paragraph_content: Mapping[Any, str],
        *,
        document_title: str,
        document_author: str,
        document_url: str,
        document_date: str,
        output_path: str,
        law_id: str,
        namespace: str | None = None,
    ) -> None:
        ns = namespace or law_id
        entries: dict[str, dict] = {}
        law = is_law_content(paragraph_content)

        if law:
            # The act itself, modelled as the shared parent of every provision.
            entries[f"{ns}:main"] = {
                "type": "Legislation",
                "title": document_title,
                "author": [document_author] if document_author else [],
                "publisher": document_author,
                "url": document_url,
                "date": document_date,
            }

        for key, content in paragraph_content.items():
            if law and isinstance(key, tuple) and len(key) == 3:
                _chapter, para, sec = key
                clean_para = "p" + para.lower().replace(" ", "")
                clean_sec = sec.lower().replace("stk. ", "stk").replace(".", "")
                para_id = f"{ns}:{clean_para}{clean_sec}"
                author = [f"{document_title} § {para} {sec}"]
                entries[para_id] = {
                    "type": "Article",
                    "title": content,
                    "author": author,
                    "publisher": document_author,
                    "url": document_url,
                    "date": document_date,
                    "parent": {
                        "type": "Legislation",
                        "title": document_title,
                        "author": [document_author] if document_author else [],
                        "date": document_date,
                        "url": document_url,
                    },
                }
            else:
                para_id = f"{law_id}_{key}"
                entries[para_id] = {
                    "type": "Article",
                    "title": content,
                    "author": [f"{document_title.capitalize()} section {key}"],
                    "publisher": document_author,
                    "url": document_url,
                    "date": document_date,
                }

        ensure_parent_dir(output_path)
        with open(output_path, "w", encoding="utf-8") as f:
            for para_id, item in entries.items():
                f.write(_watermark(item.get("url")))
                yaml.dump(
                    {para_id: item}, f, default_flow_style=False, allow_unicode=True
                )
        print(f"Written Hayagriva YAML output to {output_path}")


class MarkdownFormat:
    """Write a structured Markdown document (``.md``)."""

    def write(
        self,
        paragraph_content: Mapping[Any, str],
        *,
        document_title: str,
        document_author: str,
        document_url: str,
        document_date: str,
        output_path: str,
        law_id: str,
        namespace: str | None = None,
    ) -> None:
        # Meta fields reserved for future front-matter; structure uses title only.
        del document_author, document_url, document_date, law_id, namespace

        md_content = f"# {document_title}\n\n"

        if is_law_content(paragraph_content):
            sorted_keys = sorted(
                paragraph_content.keys(), key=lambda x: (int(x[0]), x[1], x[2])
            )
            current_chapter = None
            current_paragraph = None
            for key in sorted_keys:
                chapter, paragraph, section = key
                if chapter != current_chapter:
                    md_content += f"## Kapitel {chapter}\n\n"
                    current_chapter = chapter
                    current_paragraph = None
                if paragraph != current_paragraph:
                    md_content += f"### § {paragraph}\n\n"
                    current_paragraph = paragraph
                md_content += f"{section}: {paragraph_content[key]}\n\n"
        else:
            sorted_keys = sorted(
                paragraph_content.keys(), key=lambda x: int(x.replace("para", ""))
            )
            for key in sorted_keys:
                para_num = key.replace("para", "")
                md_content += f"### Section {para_num}\n\n{paragraph_content[key]}\n\n"

        ensure_parent_dir(output_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"Written Markdown output to {output_path}")


_BIBTEX = BibTeXFormat()
_HAYAGRIVA = HayagrivaFormat()
_MARKDOWN = MarkdownFormat()


def format_for_path(output_path: str) -> OutputFormat:
    """Pick a format adapter from the output file extension."""
    lower = output_path.lower()
    if lower.endswith((".yaml", ".yml")):
        return _HAYAGRIVA
    if lower.endswith(".md"):
        return _MARKDOWN
    return _BIBTEX
