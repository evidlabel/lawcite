from pypdf import PdfReader
from typing import Dict
import re


def parse_general_paragraphs(pdf: PdfReader) -> Dict[str, str]:
    """Parse paragraphs from a general PDF, assigning incremental IDs."""
    paragraph_content: Dict[str, str] = {}
    current_para_id = 0
    current_content = []
    in_body = False
    document_title = (
        pdf.metadata.get("/Title", "")
        if pdf.metadata and "/Title" in pdf.metadata
        else ""
    )

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
                    paragraph_content[f"para{current_para_id}"] = " ".join(
                        current_content
                    ).strip()
                    current_content = []
                continue

            if page_num == 0 and not in_body:
                if (
                    re.match(
                        r"^\d+\.\s|^[A-Z][a-z]+\s*[-–]\s*[A-Z][a-z]+|^Udskriftsdato:|^VEJ nr|^Ministerium:",
                        line,
                    )
                    or line == document_title
                ):
                    continue
                in_body = True

            if in_body:
                current_content.append(line)
                if line.endswith("."):
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not re.match(
                            r"^\d+\.\s|^\d+\.\d+\.\s", next_line
                        ):
                            current_para_id += 1
                            paragraph_content[f"para{current_para_id}"] = " ".join(
                                current_content
                            ).strip()
                            current_content = []
                        elif next_line and re.match(
                            r"^\d+\.\s|^\d+\.\d+\.\s", next_line
                        ):
                            current_para_id += 1
                            paragraph_content[f"para{current_para_id}"] = " ".join(
                                current_content
                            ).strip()
                            current_content = []

    if current_content and in_body:
        current_para_id += 1
        paragraph_content[f"para{current_para_id}"] = " ".join(current_content).strip()

    paragraph_content = {k: v for k, v in paragraph_content.items() if v}

    if not paragraph_content:
        print("Warning: No paragraphs extracted from PDF")

    return paragraph_content
