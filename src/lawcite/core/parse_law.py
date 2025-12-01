from pypdf import PdfReader
from typing import Dict, Tuple
import re


def parse_law_paragraphs(pdf: PdfReader) -> Dict[Tuple[str, str, str], str]:
    """Parse paragraphs, subsections, and chapters from a legal PDF.

    Args:
        pdf: PdfReader object containing the PDF content.

    Returns:
        Dictionary mapping (chapter, paragraph, section) tuples to content strings.
    """
    paragraph_content: Dict[Tuple[str, str, str], str] = {}
    current_chapter = None
    current_paragraph = None
    current_section = None
    skip_next = False

    for page in pdf.pages:
        text = page.extract_text()
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if skip_next:
                skip_next = False
                continue

            # Detect chapter (e.g., "Kapitel 1")
            chapter_match = re.match(r"Kapitel (\d+)", line)
            if chapter_match:
                current_chapter = chapter_match.group(1)
                skip_next = True  # Skip the next line (chapter title)
                continue

            # Detect paragraph (e.g., "§ 1.", "§ 15a.", "§ 15 a.")
            para_match = re.match(r"§ (\d+\s*[a-zA-Z]?)\.\s*(.*)", line)
            if para_match:
                current_paragraph = para_match.group(1).replace(" ", "")
                current_section = "Stk. 1."
                content = para_match.group(2).strip()
                chapter = current_chapter or "1"  # Default to chapter 1 if none detected
                key = (chapter, current_paragraph, current_section)
                paragraph_content[key] = content if content else " "
                continue

            # Detect subsection (e.g., "Stk. 2.")
            stk_match = re.match(r"Stk\. (\d+)\.\s*(.*)", line)
            if stk_match and current_paragraph:
                current_section = f"Stk. {stk_match.group(1)}."
                content = stk_match.group(2).strip()
                chapter = current_chapter or "1"
                key = (chapter, current_paragraph, current_section)
                paragraph_content[key] = content if content else " "
                continue

            # Append to current paragraph/section if applicable
            if current_paragraph and current_section:
                chapter = current_chapter or "1"
                key = (chapter, current_paragraph, current_section)
                if key in paragraph_content:
                    paragraph_content[key] += " " + line

    return paragraph_content
