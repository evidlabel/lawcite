"""Client for the structured retsinformation API (``retsinformation-api.dk``).

This replaces the old "download the law PDF and regex it" path for the ``law``
command. The API returns the whole law as a clean JSON tree (chapters →
paragraphs → stk → litra) plus tidy metadata, so we get content parity with the
PDF, gain ``litra``, and can fetch a single ``§`` for narrow lookup.

The public API is rate-limited (~5000 requests/day, shared). Two defences:

* **On-disk cache** — resolved names and fetched laws are cached under
  ``$LAWCITE_CACHE_DIR`` (default ``~/.cache/lawcite``), so repeat runs and
  narrow lookups on a law already seen cost zero API calls.
* **Rate-limit signalling** — when the API reports a rate limit we raise
  :class:`RateLimitError` so the CLI can fall back to the official
  retsinformation.dk PDF (see :func:`lawcite.api.client.eli_pdf_url`).
"""

import json
import os
import re
from pathlib import Path
from typing import Tuple

import requests

BASE_URL = "https://retsinformation-api.dk/v1"
TIMEOUT = 20

# Official retsinformation.dk eli → PDF, used as the rate-limit fallback source.
ELI_BASE = "https://www.retsinformation.dk/eli"

# A year/number identifier such as "2024/1150" (also tolerates "2024 1150").
_YEAR_NUMBER_RE = re.compile(r"^\s*(\d{4})\s*[/ ]\s*(\d+)\s*$")


class RateLimitError(Exception):
    """Raised when the retsinformation API reports a rate limit."""


def cache_dir() -> Path:
    """Return the on-disk cache directory (created on demand)."""
    path = Path(os.environ.get("LAWCITE_CACHE_DIR", Path.home() / ".cache" / "lawcite"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _is_rate_limited(resp: requests.Response) -> bool:
    """Detect a rate-limit response (HTTP 429 or a ``Rate limit …`` JSON body)."""
    if resp.status_code == 429:
        return True
    if "application/json" in resp.headers.get("Content-Type", ""):
        try:
            body = resp.json()
        except ValueError:
            return False
        if (
            isinstance(body, dict)
            and "rate limit" in str(body.get("error", "")).lower()
        ):
            return True
    return False


def eli_pdf_url(year: int, number: int, eli_type: str = "lta") -> str:
    """Official retsinformation.dk PDF URL for a law, by ELI (no API, no limit)."""
    return f"{ELI_BASE}/{eli_type}/{year}/{number}/pdf"


def eli_url(year: int, number: int, eli_type: str = "lta") -> str:
    """Human-facing retsinformation.dk page URL for a law (used as citation url)."""
    return f"{ELI_BASE}/{eli_type}/{year}/{number}"


def _resolve_cache() -> Path:
    return cache_dir() / "resolve.json"


def resolve_law(name: str, use_cache: bool = True) -> Tuple[int, int]:
    """Resolve a law name (e.g. ``"konkurrenceloven"``) to ``(year, number)``.

    Raises:
        ValueError: If no law matches, or the query is ambiguous.
        RateLimitError: If the API is rate-limited (and the name is not cached).
    """
    key = name.strip().lower()
    cache_path = _resolve_cache()
    cache = {}
    if use_cache and cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except ValueError:
            cache = {}
        if key in cache:
            year, number = cache[key]
            return int(year), int(number)

    resp = requests.get(
        f"{BASE_URL}/lovgivning/resolve", params={"q": name}, timeout=TIMEOUT
    )
    if _is_rate_limited(resp):
        raise RateLimitError(f"rate-limited resolving '{name}'")
    if resp.status_code == 404:
        raise ValueError(f"No law matched query: '{name}'")
    if resp.status_code == 300:
        candidates = resp.json().get("candidates", resp.json())
        lines = [
            f"  - {c.get('short_name', '?')} ({c.get('popular_title', '?')})"
            for c in (candidates if isinstance(candidates, list) else [])
        ]
        listing = "\n".join(lines) if lines else "  (see API for candidates)"
        raise ValueError(
            f"Ambiguous query '{name}'. Candidates:\n{listing}\n"
            "Re-run with a more specific name or a 'year/number' identifier."
        )
    resp.raise_for_status()
    data = resp.json()
    year, number = int(data["year"]), int(data["number"])
    if use_cache:
        cache[key] = [year, number]
        cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return year, number


def get_law(year: int, number: int, use_cache: bool = True) -> dict:
    """Fetch the full structured law for ``year``/``number``.

    Returns the parsed JSON (``structure`` tree plus metadata). Reads from / writes
    to the on-disk cache when ``use_cache`` is set.

    Raises:
        RateLimitError: If the API is rate-limited and the law is not cached.
    """
    cache_path = cache_dir() / f"law-{year}-{number}.json"
    if use_cache and cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except ValueError:
            pass  # corrupt cache -> re-fetch

    resp = requests.get(f"{BASE_URL}/lovgivning/{year}/{number}", timeout=TIMEOUT)
    if _is_rate_limited(resp):
        raise RateLimitError(f"rate-limited fetching law {year}/{number}")
    resp.raise_for_status()
    data = resp.json()
    if use_cache:
        cache_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def parse_identifier(identifier: str, use_cache: bool = True) -> Tuple[int, int]:
    """Turn a CLI identifier into ``(year, number)``.

    Accepts either a ``"year/number"`` string (used verbatim) or a law name
    (resolved via :func:`resolve_law`).
    """
    match = _YEAR_NUMBER_RE.match(identifier)
    if match:
        return int(match.group(1)), int(match.group(2))
    return resolve_law(identifier, use_cache=use_cache)
