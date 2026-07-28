"""
uploads/pdf_reader.py
Structured PDF extraction with OCR fallback using PyMuPDF.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _clean_text(value: str) -> str:
    return " ".join((value or "").split())


def _extract_headings(page_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    headings: List[Dict[str, Any]] = []
    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            text = _clean_text(" ".join(span.get("text", "") for span in spans))
            if not text:
                continue
            max_size = max((span.get("size", 0) for span in spans), default=0)
            is_bold = any("bold" in (span.get("font", "").lower()) for span in spans)
            if len(text) <= 120 and (max_size >= 12 or is_bold or text.isupper()):
                bbox = line.get("bbox") or spans[0].get("bbox")
                headings.append({"text": text, "bbox": bbox})
    return headings


def _extract_lists(page_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text = _clean_text(" ".join(span.get("text", "") for span in spans))
            if not text:
                continue
            if text[:2] in {"- ", "* ", "• ", "· "} or text[:3].isdigit():
                items.append({"text": text, "bbox": line.get("bbox")})
                continue
            if len(text) > 2 and text[0].isdigit() and text[1] in {".", ")", "-"}:
                items.append({"text": text, "bbox": line.get("bbox")})
    return items


def _extract_words(page, textpage=None) -> List[Dict[str, Any]]:
    words = page.get_text("words", textpage=textpage) if textpage is not None else page.get_text("words")
    return [
        {
            "text": word[4],
            "bbox": [word[0], word[1], word[2], word[3]],
            "page_number": page.number + 1,
            "block": word[5],
            "line": word[6],
            "word": word[7],
        }
        for word in words
        if len(word) >= 8 and word[4].strip()
    ]


def _extract_tables(page) -> List[Dict[str, Any]]:
    tables: List[Dict[str, Any]] = []
    try:
        finder = page.find_tables()
    except Exception:
        return tables

    for index, table in enumerate(getattr(finder, "tables", []) or []):
        try:
            tables.append({
                "index": index,
                "bbox": list(getattr(table, "bbox", []) or []),
                "rows": table.extract(),
            })
        except Exception:
            continue
    return tables


def extract_pdf_document(path: Path) -> Dict[str, Any]:
    """Extract structured content from every page in a PDF."""
    import fitz  # PyMuPDF

    doc = fitz.open(str(path))
    pages: List[Dict[str, Any]] = []
    full_text: List[str] = []
    used_ocr = False

    for page_number, page in enumerate(doc, start=1):
        try:
            page_dict = page.get_text("dict")
            textpage = None
            words = _extract_words(page)
            page_text = _clean_text(page.get_text("text"))

            if not words or len(page_text) < 20:
                textpage = page.get_textpage_ocr()
                words = _extract_words(page, textpage=textpage)
                page_text = _clean_text(page.get_text("text", textpage=textpage))
                used_ocr = True
                if textpage is not None:
                    page_dict = page.get_text("dict", textpage=textpage)

            headings = _extract_headings(page_dict)
            lists = _extract_lists(page_dict)
            tables = _extract_tables(page)

            pages.append(
                {
                    "page_number": page_number,
                    "text": page_text,
                    "words": words,
                    "headings": headings,
                    "lists": lists,
                    "tables": tables,
                    "ocr_used": bool(textpage),
                }
            )
            full_text.append(page_text)
        except Exception:
            pages.append(
                {
                    "page_number": page_number,
                    "text": "",
                    "words": [],
                    "headings": [],
                    "lists": [],
                    "tables": [],
                    "ocr_used": False,
                }
            )

    doc.close()
    return {
        "text": "\n".join(part for part in full_text if part),
        "pages": pages,
        "ocr_used": used_ocr,
        "page_count": len(pages),
        "word_count": sum(len(page["words"]) for page in pages),
    }


def extract_pdf_text(path: Path) -> str:
    return extract_pdf_document(path)["text"]
