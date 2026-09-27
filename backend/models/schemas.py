from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ProgressStage(str, Enum):
    UNDERSTANDING = "understanding"
    SELECTING_SOURCE = "selecting_source"
    SEARCHING = "searching"
    DOWNLOADING = "downloading"
    EXTRACTING = "extracting"
    BUILDING_EXCEL = "building_excel"
    FINISHED = "finished"
    ERROR = "error"


class ProgressEvent(BaseModel):
    stage: ProgressStage
    message: str
    progress: float = Field(ge=0.0, le=1.0)


class SourceInfo(BaseModel):
    id: str
    name: str
    url: str
    type: str


class DownloadedFile(BaseModel):
    name: str
    url: str
    size_bytes: int
    source_id: str
    local_path: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)


class SearchResult(BaseModel):
    id: str
    query: str
    summary: str
    sources_consulted: list[SourceInfo]
    downloaded_files: list[DownloadedFile]
    table_preview: list[dict[str, Any]]
    excel_path: str | None = None
    status: str
    created_at: datetime
    messages: list[str] = Field(default_factory=list)


class HistoryItem(BaseModel):
    id: str
    query: str
    status: str
    created_at: datetime
    sources_count: int
    files_count: int
