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


_STK_RE = re.compile(r"Stk\.\s*(\d+)", re.IGNORECASE)
_ITEM_RE = re.compile(r"\b(nr\.|litra)\s*([0-9a-zæøå]+)\s*$", re.IGNORECASE)


def split_section(section: str) -> tuple[str, str, str]:
    """``"Stk. 2. nr. 3"`` -> ``("2", "nr.", "3")``; ``"Stk. 1."`` -> ``("1", "", "")``."""
    stk = _STK_RE.search(section or "")
    item = _ITEM_RE.search(section or "")
    return (
        stk.group(1) if stk else "",
        item.group(1).lower() if item else "",
        item.group(2).lower() if item else "",
    )


def section_slug(section: str) -> str:
    """The key part of a section: ``"Stk. 2."`` -> ``"stk2"``, ``"Stk. 1. nr. 3"`` -> ``"stk1nr3"``."""
    stk, kind, item = split_section(section)
    if not stk:  # not a Stk. label: the old rule
        return section.lower().replace("stk. ", "stk").replace(".", "").replace(" ", "")
    return f"stk{stk}" + (f"{kind.rstrip('.')}{item}" if kind else "")


def stk_counts(paragraph_content: Mapping[Any, str]) -> dict[str, int]:
    """How many stk each § has, counting stk entries only (not their items)."""
    stks: dict[str, set[str]] = {}
    for key in paragraph_content:
        _chapter, para, section = key
        stk, kind, _item = split_section(section)
        if not kind:
            stks.setdefault(para, set()).add(stk or section)
    return {para: len(s) for para, s in stks.items()}


def cite_label(para: str, section: str, n_stk: int) -> str:
    """How the provision is cited: ``§ 7`` (one stk), ``§ 7, stk. 2``, ``§ 3, stk. 1, nr. 2``.

    The first stk of a § carries no "Stk. 1." label in the act, so a § with a
    single stk is cited by its § alone.
    """
    stk, kind, item = split_section(section)
    label = f"§ {para}"
    if stk and n_stk > 1:
        label += f", stk. {stk}"
    elif not stk:
        label += f" {section}"
    if kind:
        label += f", {kind} {item}"
    return label
