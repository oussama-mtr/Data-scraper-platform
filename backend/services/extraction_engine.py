from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd


def _extract_pdf(path: Path) -> list[dict[str, Any]]:
    try:
        import pdfplumber
    except ImportError:
        return [{"content": "PDF extraction unavailable (pdfplumber not installed)."}]

    rows: list[dict[str, Any]] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages[:5], start=1):
            text = (page.extract_text() or "").strip()
            if text:
                rows.append({"page": page_number, "content": text[:1200]})
            tables = page.extract_tables() or []
            for table_index, table in enumerate(tables[:2], start=1):
                for table_row in table[:20]:
                    if table_row and any(cell for cell in table_row):
                        rows.append(
                            {
                                "page": page_number,
                                "table": table_index,
                                "row": [cell or "" for cell in table_row],
                            }
                        )
    return rows


def _extract_spreadsheet(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(path)
    else:
        frame = pd.read_excel(path)

    frame = frame.head(50)
    return frame.fillna("").to_dict(orient="records")


def extract_from_documents(files: list[dict]) -> list[dict[str, Any]]:
    extracted: list[dict[str, Any]] = []
    for file_info in files:
        local_path = file_info.get("local_path")
        if not local_path:
            continue

        path = Path(local_path)
        if not path.exists():
            continue

        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                rows = _extract_pdf(path)
            elif suffix in {".xls", ".xlsx", ".csv"}:
                rows = _extract_spreadsheet(path)
            else:
                rows = [{"content": path.read_text(encoding="utf-8", errors="ignore")[:1200]}]
        except Exception as exc:
            rows = [{"error": str(exc), "file": file_info["name"]}]

        extracted.append(
            {
                "file": file_info["name"],
                "source_id": file_info["source_id"],
                "rows": rows,
            }
        )
    return extracted


def build_table_preview(extracted: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    preview: list[dict[str, Any]] = []
    for item in extracted:
        for row in item.get("rows", []):
            if isinstance(row, dict):
                preview.append({"source_file": item["file"], **row})
            if len(preview) >= limit:
                return preview
    return preview


def build_excel(extracted: list[dict[str, Any]], output_path: Path) -> str | None:
    if not extracted:
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for index, item in enumerate(extracted, start=1):
            rows = item.get("rows", [])
            if not rows:
                continue
            frame = pd.json_normalize(rows)
            sheet_name = f"Doc_{index}"[:31]
            frame.to_excel(writer, sheet_name=sheet_name, index=False)

    return str(output_path)


def summarize_extraction(query: str, extracted: list[dict[str, Any]], sources: list[dict]) -> str:
    if not extracted:
        return (
            "No matching public document was found on the selected official sources. "
            "Try refining your query with a company name, document type, or time period."
        )

    source_names = ", ".join(source["name"] for source in sources)
    file_count = sum(len(item.get("rows", [])) for item in extracted)
    return (
        f"Processed your request: \"{query}\". "
        f"Consulted official sources: {source_names}. "
        f"Extracted structured content from {len(extracted)} file(s) "
        f"with {file_count} data segment(s). Review the table preview and download the Excel export."
    )
