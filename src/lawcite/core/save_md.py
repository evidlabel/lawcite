import os
from typing import Dict


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
        law_id: Cleaned law ID.
        output_filename: Output file path.
    """
    md_content = f"# {document_title}\n\n"

    if isinstance(paragraph_content, dict) and all(isinstance(k, tuple) and len(k) == 3 for k in paragraph_content):
        # Law: sort by chapter, paragraph, section
        sorted_keys = sorted(paragraph_content.keys(), key=lambda x: (int(x[0]), x[1], x[2]))
        current_chapter = None
        current_paragraph = None
        for key in sorted_keys:
            chapter, paragraph, section = key
            if chapter != current_chapter:
                md_content += f"## Kapitel {chapter}\n\n"
                current_chapter = chapter
                current_paragraph = None  # Reset paragraph on new chapter
            if paragraph != current_paragraph:
                md_content += f"### § {paragraph}\n\n"
                current_paragraph = paragraph
            md_content += f"{section}: {paragraph_content[key]}\n\n"
    else:
        # General: sort by paragraph ID
        sorted_keys = sorted(paragraph_content.keys(), key=lambda x: int(x.replace('para', '')))
        for key in sorted_keys:
            para_num = key.replace('para', '')
            md_content += f"### Paragraph {para_num}\n\n{paragraph_content[key]}\n\n"

    # Ensure directory exists
    dir_path = os.path.dirname(output_filename)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Written Markdown output to {output_filename}")
