from pypdf import PdfReader
from typing import Dict, Tuple
import re


def parse_law_paragraphs(pdf: PdfReader) -> Dict[Tuple[str, str], str]:
    """Parse paragraphs and subsections from a legal PDF.

    Args:
        pdf: PdfReader object containing the PDF content.

    Returns:
        Dictionary mapping (paragraph, section) tuples to content strings.
    """
    paragraph_content: Dict[Tuple[str, str], str] = {}
    current_paragraph = None
    current_section = None

    for page in pdf.pages:
        text = page.extract_text()
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect paragraph (e.g., "§ 1.", "§ 15a.", "§ 15 a.")
            para_match = re.match(r"§ (\d+\s*[a-zA-Z]?)\.\s*(.*)", line)
            if para_match:
                current_paragraph = para_match.group(1).replace(" ", "")
                current_section = "Stk. 1."
                content = para_match.group(2).strip()
                key = (current_paragraph, current_section)
                paragraph_content[key] = content if content else " "
                continue

            # Detect subsection (e.g., "Stk. 2.")
            stk_match = re.match(r"Stk\. (\d+)\.\s*(.*)", line)
            if stk_match and current_paragraph:
                current_section = f"Stk. {stk_match.group(1)}."
                content = stk_match.group(2).strip()
                key = (current_paragraph, current_section)
                paragraph_content[key] = content if content else " "
                continue

            # Append to current paragraph/section if applicable
            if current_paragraph and current_section:
                key = (current_paragraph, current_section)
                if key in paragraph_content:
                    paragraph_content[key] += " " + line

    return paragraph_content
