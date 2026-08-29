"""Thin save dispatcher and backward-compatible ``save_bibtex`` alias.

Format-specific serialization lives in :mod:`lawcite.save.formats`. Call
:func:`save` (preferred) or :func:`save_bibtex` (legacy name).
"""

from __future__ import annotations

from typing import Dict

from .common import law_id_from_title
from .formats import format_for_path


def save(
    paragraph_content: Dict,
    document_title: str,
    document_author: str,
    document_url: str,
    document_date: str,
    output_path: str = "__temp.bib",
    namespace: str | None = None,
) -> None:
    """Save bibliography / document text; format chosen by file extension.

    Args:
        paragraph_content: Dictionary of paragraph content (law triples or
            general ``paraN`` keys).
        document_title: Title of the document.
        document_author: Author of the document.
        document_url: URL of the document.
        document_date: Date of the document.
        output_path: Output file path. Extension selects the adapter:
            ``.yaml``/``.yml`` → Hayagriva, ``.md`` → Markdown, else BibTeX.
            Empty string falls back to ``{law_id}.bib``.
        namespace: Hayagriva key namespace for laws (e.g. ``"lbk2024-1150"``).
            When set, law keys become ``<namespace>:p9stk1``, an extra
            ``<namespace>:main`` entry describes the whole act, and every
            provision carries a ``parent`` pointing at that act. Ignored for
            the general (non-law) path and for non-YAML formats.
    """
    law_id = law_id_from_title(document_title)
    path = output_path if output_path else f"{law_id}.bib"
    fmt = format_for_path(path)
    fmt.write(
        paragraph_content,
        document_title=document_title,
        document_author=document_author,
        document_url=document_url,
        document_date=document_date,
        output_path=path,
        law_id=law_id,
        namespace=namespace,
    )


def save_bibtex(
    paragraph_content: Dict,
    document_title: str,
    document_author: str,
    document_url: str,
    document_date: str,
    output_filename: str = "__temp.bib",
    namespace: str | None = None,
) -> None:
    """Legacy name for :func:`save` (``output_filename`` → ``output_path``)."""
    save(
        paragraph_content,
        document_title,
        document_author,
        document_url,
        document_date,
        output_path=output_filename,
        namespace=namespace,
    )
