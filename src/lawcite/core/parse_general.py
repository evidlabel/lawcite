from pypdf import PdfReader
from typing import Dict
import re

def parse_general_paragraphs(pdf: PdfReader) -> Dict[str, str]:
    """Parse paragraphs from a general PDF, assigning incremental IDs.

    Args:
        pdf: PdfReader object containing the PDF content.

    Returns:
        Dictionary mapping paragraph IDs (e.g., para1, para2) to content strings.
    """
    paragraph_content: Dict[str, str] = {}
    current_para_id = 0
    current_content = []
    in_body = False

    for page_num, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text:
            continue
        lines = text.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                if current_content and in_body:
                    current_para_id += 1
                    paragraph_content[f"para{current_para_id}"] = " ".join(current_content).strip()
                    current_content = []
                continue

            # Skip metadata on first page until body text starts
            if page_num == 0 and not in_body:
                if re.match(r"^\d+\.\s|^[A-Z][a-z]+\s*[-–]\s*[A-Z][a-z]+|^Udskriftsdato:|^VEJ nr|^Ministerium:", line):
                    continue
                in_body = True

            # Detect paragraph break: line ends with a period and the next line (if any) exists
            if in_body:
                current_content.append(line)
                # Check if the line ends with a period
                if line.endswith("."):
                    # Check if there's a next line (i.e., not the last line)
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        # If the next line exists and is not empty, this is a paragraph break
                        if next_line and not re.match(r"^\d+\.\s|^\d+\.\d+\.\s", next_line):
                            current_para_id += 1
                            paragraph_content[f"para{current_para_id}"] = " ".join(current_content).strip()
                            current_content = []
                        # If the next line is a numbered section (e.g., "1.", "2.1."), also break
                        elif next_line and re.match(r"^\d+\.\s|^\d+\.\d+\.\s", next_line):
                            current_para_id += 1
                            paragraph_content[f"para{current_para_id}"] = " ".join(current_content).strip()
                            current_content = []

    # Save any remaining content as the last paragraph
    if current_content and in_body:
        current_para_id += 1
        paragraph_content[f"para{current_para_id}"] = " ".join(current_content).strip()

    # Remove empty paragraphs
    paragraph_content = {k: v for k, v in paragraph_content.items() if v}

    if not paragraph_content:
        print("Warning: No paragraphs extracted from PDF")

    return paragraph_content
