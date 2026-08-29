"""Shared helpers for bibliography / document output formats."""

from __future__ import annotations

import os
import re
from typing import Any, Mapping

from unidecode import unidecode


def is_law_content(paragraph_content: Mapping[Any, str] | dict) -> bool:
    """Return True when keys are ``(chapter, paragraph, section)`` triples.

    Used to distinguish law-style paragraph maps from general ``paraN`` maps
    without a dedicated Paragraph dataclass.
    """
    if not isinstance(paragraph_content, dict) or not paragraph_content:
        return False
    return all(isinstance(k, tuple) and len(k) == 3 for k in paragraph_content)


def law_id_from_title(document_title: str) -> str:
    """Slugify a document title into a stable ASCII identifier."""
    title_lower = unidecode(document_title).lower()
    return re.sub(r"[^a-z0-9]+", "", title_lower)


def ensure_parent_dir(path: str) -> None:
    """Create the parent directory of ``path`` if it is non-empty and missing."""
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
