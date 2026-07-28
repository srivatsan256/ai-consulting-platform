"""
uploads/docx_reader.py
DOCX/DOC text extraction using python-docx.
"""
from pathlib import Path


def extract_docx_text(path: Path) -> str:
    """Extract all paragraph text from a DOCX file."""
    from docx import Document

    doc = Document(str(path))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)
