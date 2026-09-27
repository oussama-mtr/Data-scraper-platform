from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from backend.agents.search_agent import SearchAgent
from backend.config.sources import SOURCES
from backend.models.schemas import SearchRequest
from backend.services.history_store import get_result, list_downloaded_files, list_history, save_result

router = APIRouter(prefix="/api", tags=["search"])
agent = SearchAgent()


@router.get("/sources")
def get_sources():
    return {"sources": SOURCES}


@router.get("/history")
def get_history():
    return {"items": list_history()}


@router.get("/downloads")
def get_downloads():
    return {"files": list_downloaded_files()}


@router.get("/results/{search_id}")
def get_search_result(search_id: str):
    result = get_result(search_id)
    if not result:
        raise HTTPException(status_code=404, detail="Search result not found")
    return result


@router.get("/results/{search_id}/excel")
def download_excel(search_id: str):
    result = get_result(search_id)
    if not result or not result.excel_path:
        raise HTTPException(status_code=404, detail="Excel export not available")

    excel_path = Path(result.excel_path)
    if not excel_path.exists():
        raise HTTPException(status_code=404, detail="Excel file missing on disk")

    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"mai-finance-{search_id}.xlsx",
    )


@router.post("/search/stream")
async def stream_search(request: SearchRequest):
    async def event_generator():
        events: list[dict] = []

        def on_progress(event):
            events.append(event.model_dump())

        result = agent.run(request.query, on_progress=on_progress)
        save_result(result)

        for event in events:
            yield {"event": "progress", "data": json.dumps(event)}

        yield {"event": "result", "data": json.dumps(result.model_dump(mode="json"))}

    return EventSourceResponse(event_generator())
