from __future__ import annotations

from backend.models.schemas import HistoryItem, SearchResult

_results: dict[str, SearchResult] = {}


def save_result(result: SearchResult) -> SearchResult:
    _results[result.id] = result
    return result


def get_result(search_id: str) -> SearchResult | None:
    return _results.get(search_id)


def list_history() -> list[HistoryItem]:
    items = sorted(_results.values(), key=lambda result: result.created_at, reverse=True)
    return [
        HistoryItem(
            id=result.id,
            query=result.query,
            status=result.status,
            created_at=result.created_at,
            sources_count=len(result.sources_consulted),
            files_count=len(result.downloaded_files),
        )
        for result in items
    ]


def list_downloaded_files() -> list[dict]:
    files: list[dict] = []
    for result in _results.values():
        for file in result.downloaded_files:
            files.append(
                {
                    "search_id": result.id,
                    "query": result.query,
                    "name": file.name,
                    "url": file.url,
                    "source_id": file.source_id,
                    "size_bytes": file.size_bytes,
                    "created_at": result.created_at.isoformat(),
                }
            )
    return sorted(files, key=lambda item: item["created_at"], reverse=True)
