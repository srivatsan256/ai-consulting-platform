"""
uploads/parser.py
Universal document text extractor.
Dispatches to the appropriate reader based on file extension.
"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str) -> str:
    """
    Extract plain text from a PDF, DOCX, or XLSX file.

    Args:
        file_path: Absolute path to the uploaded file.

    Returns:
        Extracted text string, or empty string on failure.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    try:
        if ext == ".pdf":
            from .pdf_reader import extract_pdf_text
            return extract_pdf_text(path)

        elif ext in (".docx", ".doc"):
            from .docx_reader import extract_docx_text
            return extract_docx_text(path)

        elif ext in (".xlsx", ".xls"):
            from .xlsx_reader import extract_xlsx_text
            return extract_xlsx_text(path)

        elif ext in (".txt",):
            return path.read_text(encoding="utf-8", errors="replace")

        else:
            logger.warning("Unsupported file type: %s", ext)
            return ""

    except Exception as exc:
        logger.error("Text extraction failed for %s: %s", file_path, exc)
        return ""


def extract_document_from_file(file_path: str) -> dict:
    """Return structured extraction data when available."""
    path = Path(file_path)
    ext = path.suffix.lower()

    try:
        if ext == ".pdf":
            from .pdf_reader import extract_pdf_document
            return extract_pdf_document(path)

        return {
            "text": extract_text_from_file(file_path),
            "pages": [],
            "ocr_used": False,
            "page_count": 0,
            "word_count": 0,
        }
    except Exception as exc:
        logger.error("Structured extraction failed for %s: %s", file_path, exc)
        return {"text": "", "pages": [], "ocr_used": False, "page_count": 0, "word_count": 0}
