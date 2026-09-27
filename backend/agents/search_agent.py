from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from backend.config.sources import SourceConfig
from backend.models.schemas import (
    DownloadedFile,
    ProgressEvent,
    ProgressStage,
    SearchResult,
    SourceInfo,
)
from backend.services.document_downloader import download_documents
from backend.services.extraction_engine import (
    build_excel,
    build_table_preview,
    extract_from_documents,
    summarize_extraction,
)
from backend.services.site_crawler import search_official_site
from backend.services.source_selector import select_relevant_sources

ProgressCallback = Callable[[ProgressEvent], None]


class SearchAgent:
    def run(self, query: str, on_progress: ProgressCallback | None = None) -> SearchResult:
        search_id = str(uuid.uuid4())
        messages: list[str] = []

        def emit(stage: ProgressStage, message: str, progress: float) -> None:
            messages.append(message)
            if on_progress:
                on_progress(ProgressEvent(stage=stage, message=message, progress=progress))

        emit(ProgressStage.UNDERSTANDING, "Understanding request...", 0.05)

        sources = select_relevant_sources(query)
        if not sources:
            emit(
                ProgressStage.ERROR,
                "No relevant official source could be determined from the centralized configuration.",
                1.0,
            )
            return self._empty_result(search_id, query, messages)

        emit(
            ProgressStage.SELECTING_SOURCE,
            f"Selecting official source: {', '.join(source['name'] for source in sources)}...",
            0.15,
        )

        all_documents: list[str] = []
        consulted_sources: list[SourceConfig] = []

        for index, source in enumerate(sources):
            progress = 0.2 + (0.25 * index)
            emit(
                ProgressStage.SEARCHING,
                f"Searching {source['name']}...",
                progress,
            )
            _, documents = search_official_site(source, query)
            if documents:
                consulted_sources.append(source)
                all_documents.extend(documents)

        if not all_documents:
            emit(
                ProgressStage.FINISHED,
                "No matching public document was found on the selected official websites.",
                1.0,
            )
            return SearchResult(
                id=search_id,
                query=query,
                summary=(
                    "No matching public document was found on the official sources defined in "
                    "the centralized configuration. The search was limited to official domains only."
                ),
                sources_consulted=[self._to_source_info(source) for source in sources],
                downloaded_files=[],
                table_preview=[],
                excel_path=None,
                status="not_found",
                created_at=datetime.now(timezone.utc),
                messages=messages,
            )

        emit(ProgressStage.DOWNLOADING, "Downloading documents...", 0.55)
        downloaded_files: list[dict] = []
        for source in consulted_sources or sources:
            source_docs = [
                url for url in all_documents if source["domain"] in url
            ][:5]
            downloaded_files.extend(download_documents(source_docs, source["id"]))

        emit(ProgressStage.EXTRACTING, "Extracting data...", 0.75)
        extracted = extract_from_documents(downloaded_files)
        table_preview = build_table_preview(extracted)

        emit(ProgressStage.BUILDING_EXCEL, "Building Excel...", 0.9)
        excel_path = build_excel(
            extracted,
            Path("backend/data/exports") / f"{search_id}.xlsx",
        )

        summary = summarize_extraction(
            query,
            extracted,
            consulted_sources or sources,
        )
        emit(ProgressStage.FINISHED, "Finished.", 1.0)

        return SearchResult(
            id=search_id,
            query=query,
            summary=summary,
            sources_consulted=[
                self._to_source_info(source) for source in (consulted_sources or sources)
            ],
            downloaded_files=[DownloadedFile(**file_info) for file_info in downloaded_files],
            table_preview=table_preview,
            excel_path=excel_path,
            status="completed" if extracted else "partial",
            created_at=datetime.now(timezone.utc),
            messages=messages,
        )

    @staticmethod
    def _to_source_info(source: SourceConfig) -> SourceInfo:
        return SourceInfo(
            id=source["id"],
            name=source["name"],
            url=source["url"],
            type=source["type"],
        )

    @staticmethod
    def _empty_result(search_id: str, query: str, messages: list[str]) -> SearchResult:
        return SearchResult(
            id=search_id,
            query=query,
            summary="Unable to process the request with configured official sources.",
            sources_consulted=[],
            downloaded_files=[],
            table_preview=[],
            excel_path=None,
            status="error",
            created_at=datetime.now(timezone.utc),
            messages=messages,
        )
