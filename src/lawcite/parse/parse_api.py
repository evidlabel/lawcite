"""Parse the structured law JSON from :mod:`lawcite.api.client`.

Produces a ``Dict[(chapter, paragraph, section), text]`` that the BibTeX and
Markdown writers consume directly. On top of the raw structure it folds
``litra`` sub-points inline and supports an optional narrow-lookup ``selector``.
"""

import re
from typing import Dict, Optional, Set, Tuple

# "§ 9.", "§ 15 a." -> "9", "15a"
_PARA_RE = re.compile(r"§\s*(\d+\s*[a-zA-Z]?)")
# leading integer of "Kapitel 1", "Kapitel 3 a" -> "1", "3"
_CHAPTER_RE = re.compile(r"(\d+)")


def _norm_para(raw: str) -> str:
    """Normalise a paragraph label to its bare id, e.g. ``"§ 15 a."`` -> ``"15a"``."""
    match = _PARA_RE.search(raw or "")
    if not match:
        return (raw or "").strip()
    return match.group(1).replace(" ", "").lower()


def _fold_litra(stk: dict) -> str:
    """Return the stk text with any litra (a, b, c sub-points) folded inline."""
    text = (stk.get("text") or "").strip()
    for litra in stk.get("litra") or []:
        number = (litra.get("number") or "").strip()
        ltext = (litra.get("text") or "").strip()
        piece = " ".join(p for p in (number, ltext) if p)
        if piece:
            text = f"{text} {piece}".strip()
    return text


def parse_selector(spec: Optional[str]) -> Optional[Set[str]]:
    """Parse a narrow-lookup spec into a set of normalised paragraph ids.

    Accepts ``"9"``, ``"9-12"`` (inclusive numeric range), ``"9,11,15a"``
    (comma list, letters allowed in list items), and combinations
    (``"9-12,20"``). Returns ``None`` for an empty spec, meaning "keep all".
    """
    if not spec or not spec.strip():
        return None
    wanted: Set[str] = set()
    for part in spec.split(","):
        part = part.strip().lower().replace(" ", "")
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            if lo.isdigit() and hi.isdigit():
                wanted.update(str(n) for n in range(int(lo), int(hi) + 1))
            else:  # non-numeric range bound -> treat literally
                wanted.add(part)
        else:
            wanted.add(part)
    return wanted


def filter_by_selector(
    paragraph_content: Dict[Tuple[str, str, str], str], selector: Optional[Set[str]]
) -> Dict[Tuple[str, str, str], str]:
    """Keep only entries whose paragraph id is in ``selector`` (``None`` keeps all).

    Shared by the API path and the PDF fallback so narrow lookup behaves
    identically regardless of source. Paragraph ids are compared normalised
    (lowercased, spaces stripped), matching :func:`parse_selector`.
    """
    if selector is None:
        return paragraph_content
    return {
        (ch, para, sec): text
        for (ch, para, sec), text in paragraph_content.items()
        if para.replace(" ", "").lower() in selector
    }


def parse_law_structure(
    law_json: dict, selector: Optional[Set[str]] = None
) -> Dict[Tuple[str, str, str], str]:
    """Walk ``law_json['structure']`` into ``{(chapter, paragraph, stk): text}``.

    Args:
        law_json: The full law JSON returned by :func:`lawcite.api.client.get_law`.
        selector: Optional set of paragraph ids (from :func:`parse_selector`) to
            keep. ``None`` keeps every paragraph.
    """
    paragraph_content: Dict[Tuple[str, str, str], str] = {}
    structure = law_json.get("structure") or {}

    for chapter in structure.get("chapters") or []:
        ch_match = _CHAPTER_RE.search(chapter.get("chapter_number") or "")
        chapter_id = ch_match.group(1) if ch_match else "1"

        for group in chapter.get("paragraph_groups") or []:
            for para in group.get("paragraphs") or []:
                para_id = _norm_para(para.get("number") or "")
                for stk in para.get("stk") or []:
                    section = (stk.get("number") or "Stk. 1.").strip()
                    paragraph_content[(chapter_id, para_id, section)] = _fold_litra(stk)

    return filter_by_selector(paragraph_content, selector)


def derive_namespace(short_name: str, year, number) -> str:
    """Derive the default Hayagriva key namespace, e.g. ``"lbk2024-1150"``.

    Uses the leading token of ``short_name`` (the document-type abbreviation
    such as ``LBK``/``LOV``/``BEK``) plus ``year``-``number``. Falls back to a
    bare ``year-number`` when ``short_name`` has no usable leading token.
    """
    token = ""
    if short_name:
        first = short_name.split()[0] if short_name.split() else ""
        token = re.sub(r"[^a-z0-9]", "", first.lower())
    stem = f"{year}-{number}"
    return f"{token}{stem}" if token else stem


def metadata_from_api(law_json: dict) -> dict:
    """Map the law JSON metadata to lawcite's document fields.

    Returns a dict with ``document_title``, ``document_author``,
    ``document_url``, ``document_date``, plus ``short_name``/``year``/``number``
    used for namespace derivation.
    """
    eli = law_json.get("eli_uri") or ""
    url = f"https://www.retsinformation.dk{eli}" if eli else ""
    return {
        "document_title": law_json.get("popular_title") or law_json.get("title") or "",
        "document_author": law_json.get("ministry") or law_json.get("ressort") or "",
        "document_url": url,
        "document_date": law_json.get("signature_date") or "",
        "short_name": law_json.get("short_name") or "",
        "year": law_json.get("year"),
        "number": law_json.get("number"),
    }
