"""Output adapters and the thin save dispatcher."""

from .save_bibtex import save, save_bibtex
from .save_md import save_markdown

__all__ = ["save", "save_bibtex", "save_markdown"]
