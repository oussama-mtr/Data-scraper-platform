"""Extract tabular data from user-uploaded financial documents."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re

import pandas as pd


SUPPORTED_FILE_TYPES = ("pdf", "xlsx", "xls", "csv")


def _clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Discard fully empty rows/columns and give every column a usable name."""
    frame = frame.dropna(axis=0, how="all").dropna(axis=1, how="all").copy()
    if frame.empty:
        return frame

    frame = frame.fillna("")
    frame.columns = [
        str(column).strip() if str(column).strip() else f"Column {index + 1}"
        for index, column in enumerate(frame.columns)
    ]
    return frame


def _table_to_frame(table: list[list[str | None]]) -> pd.DataFrame:
    rows = [[cell.strip() if isinstance(cell, str) else "" for cell in row] for row in table]
    rows = [row for row in rows if any(row)]
    if not rows:
        return pd.DataFrame()

    header = rows[0]
    header = [value or f"Column {index + 1}" for index, value in enumerate(header)]
    # Duplicate headers make Excel exports difficult to work with.
    seen: dict[str, int] = {}
    unique_header = []
    for value in header:
        seen[value] = seen.get(value, 0) + 1
        unique_header.append(value if seen[value] == 1 else f"{value}_{seen[value]}")
    return _clean_frame(pd.DataFrame(rows[1:], columns=unique_header))


def _extract_pdf(file_bytes: bytes) -> list[tuple[str, pd.DataFrame]]:
    try:
        import pdfplumber
    except ImportError as exc:  # pragma: no cover - dependency error is shown to the user
        raise RuntimeError("PDF table extraction requires pdfplumber.") from exc

    tables: list[tuple[str, pd.DataFrame]] = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            for table_number, table in enumerate(page.extract_tables() or [], start=1):
                frame = _table_to_frame(table)
                if not frame.empty:
                    tables.append((f"Page {page_number} table {table_number}", frame))
    return tables


def extract_tables(filename: str, file_bytes: bytes) -> list[tuple[str, pd.DataFrame]]:
    """Recognise tables in a PDF, CSV, or spreadsheet upload."""
    extension = Path(filename).suffix.lower().lstrip(".")
    if extension not in SUPPORTED_FILE_TYPES:
        raise ValueError("Upload a PDF, CSV, XLS, or XLSX file.")

    if extension == "pdf":
        return _extract_pdf(file_bytes)
    if extension == "csv":
        return [("Table 1", _clean_frame(pd.read_csv(BytesIO(file_bytes))))]

    workbook = pd.read_excel(BytesIO(file_bytes), sheet_name=None)
    return [
        (sheet_name, cleaned)
        for sheet_name, frame in workbook.items()
        if not (cleaned := _clean_frame(frame)).empty
    ]


def build_excel_workbook(tables: list[tuple[str, pd.DataFrame]]) -> bytes:
    """Create one .xlsx workbook with one recognised table per worksheet."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        used_names: set[str] = set()
        for index, (name, frame) in enumerate(tables, start=1):
            safe_name = re.sub(r"[\\\\/*?:\[\]]", "_", name)[:28] or f"Table_{index}"
            sheet_name = safe_name
            suffix = 2
            while sheet_name in used_names:
                sheet_name = f"{safe_name[:27]}_{suffix}"
                suffix += 1
            used_names.add(sheet_name)
            frame.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()
