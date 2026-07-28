"""
uploads/xlsx_reader.py
Excel text extraction using openpyxl.
Iterates all sheets and joins cell values as text.
"""
from pathlib import Path


def extract_xlsx_text(path: Path) -> str:
    """Extract all cell values from an XLSX file across all sheets."""
    import openpyxl

    wb = openpyxl.load_workbook(str(path), data_only=True)
    rows = []
    for sheet in wb.worksheets:
        rows.append(f"=== Sheet: {sheet.title} ===")
        for row in sheet.iter_rows(values_only=True):
            row_text = "\t".join(str(cell) for cell in row if cell is not None)
            if row_text.strip():
                rows.append(row_text)
    wb.close()
    return "\n".join(rows)
