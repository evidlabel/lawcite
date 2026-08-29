"""Markdown save entry point (thin wrapper over :class:`MarkdownFormat`)."""

from __future__ import annotations

from typing import Dict

from .formats import MarkdownFormat

_markdown = MarkdownFormat()


def save_markdown(
    paragraph_content: Dict,
    document_title: str,
    document_author: str,
    document_url: str,
    document_date: str,
    law_id: str,
    output_filename: str,
) -> None:
    """Save the full document text to a Markdown file, structured for LLM input.

    Args:
        paragraph_content: Dictionary of paragraph content.
        document_title: Title of the document.
        document_author: Author of the document.
        document_url: URL of the document.
        document_date: Date of the document.
        law_id: Cleaned law ID (kept for API compatibility; unused in body).
        output_filename: Output file path.
    """
    _markdown.write(
        paragraph_content,
        document_title=document_title,
        document_author=document_author,
        document_url=document_url,
        document_date=document_date,
        output_path=output_filename,
        law_id=law_id,
    )
