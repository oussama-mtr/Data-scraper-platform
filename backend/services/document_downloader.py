from __future__ import annotations

import hashlib
from pathlib import Path

import httpx

DOWNLOAD_DIR = Path("backend/data/downloads")
USER_AGENT = (
    "Mozilla/5.0 (compatible; MAiFinanceBot/1.0; +https://github.com/ai-finance-platform)"
)


def _safe_filename(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    suffix = Path(urlparse_path(url)).suffix.lower()
    return f"{digest}{suffix}"


def urlparse_path(url: str) -> str:
    from urllib.parse import urlparse

    return urlparse(url).path


def download_documents(urls: list[str], source_id: str) -> list[dict]:
    target_dir = DOWNLOAD_DIR / source_id
    target_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[dict] = []

    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(timeout=30.0, follow_redirects=True, headers=headers) as client:
        for url in urls:
            filename = _safe_filename(url)
            local_path = target_dir / filename
            if local_path.exists():
                downloaded.append(
                    {
                        "name": filename,
                        "url": url,
                        "size_bytes": local_path.stat().st_size,
                        "source_id": source_id,
                        "local_path": str(local_path),
                    }
                )
                continue

            try:
                response = client.get(url)
                response.raise_for_status()
                local_path.write_bytes(response.content)
                downloaded.append(
                    {
                        "name": filename,
                        "url": url,
                        "size_bytes": len(response.content),
                        "source_id": source_id,
                        "local_path": str(local_path),
                    }
                )
            except httpx.HTTPError:
                continue

    return downloaded
