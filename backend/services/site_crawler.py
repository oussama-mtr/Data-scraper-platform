from __future__ import annotations

import re
from collections import deque
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from backend.config.sources import DOWNLOADABLE_EXTENSIONS, SourceConfig

USER_AGENT = (
    "Mozilla/5.0 (compatible; MAiFinanceBot/1.0; +https://github.com/ai-finance-platform)"
)
MAX_PAGES_PER_SOURCE = 25
REQUEST_TIMEOUT = 15.0


def _is_same_domain(url: str, domain: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return host == domain or host.endswith(f".{domain}")


def _is_downloadable(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in DOWNLOADABLE_EXTENSIONS)


def _normalize_url(base_url: str, href: str) -> str | None:
    if not href or href.startswith(("mailto:", "javascript:", "#")):
        return None
    absolute = urljoin(base_url, href.split("#")[0].strip())
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    return absolute


def _page_relevance(query: str, text: str, url: str) -> float:
    query_tokens = {token for token in re.findall(r"[a-z0-9]+", query.lower()) if len(token) > 2}
    haystack = f"{text} {url}".lower()
    return float(sum(1 for token in query_tokens if token in haystack))


def search_official_site(
    source: SourceConfig,
    query: str,
    max_documents: int = 8,
) -> tuple[list[str], list[str]]:
    """Search only within an official domain. Returns (page_urls, document_urls)."""
    domain = source["domain"]
    start_url = source["url"]
    visited_pages: set[str] = set()
    page_urls: list[str] = []
    document_urls: list[str] = []
    queue: deque[str] = deque([start_url])

    headers = {"User-Agent": USER_AGENT}

    with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
        while queue and len(visited_pages) < MAX_PAGES_PER_SOURCE:
            current = queue.popleft()
            if current in visited_pages or not _is_same_domain(current, domain):
                continue

            visited_pages.add(current)

            try:
                response = client.get(current)
                response.raise_for_status()
            except httpx.HTTPError:
                continue

            content_type = response.headers.get("content-type", "").lower()
            if _is_downloadable(current):
                document_urls.append(current)
                if len(document_urls) >= max_documents:
                    break
                continue

            if "html" not in content_type and "text" not in content_type:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(" ", strip=True)
            relevance = _page_relevance(query, page_text, current)
            if relevance > 0:
                page_urls.append(current)

            for anchor in soup.find_all("a", href=True):
                linked = _normalize_url(current, anchor["href"])
                if not linked or not _is_same_domain(linked, domain):
                    continue

                anchor_text = anchor.get_text(" ", strip=True)
                link_relevance = _page_relevance(query, f"{anchor_text} {linked}", linked)

                if _is_downloadable(linked):
                    if link_relevance > 0 and linked not in document_urls:
                        document_urls.append(linked)
                        if len(document_urls) >= max_documents:
                            break
                elif linked not in visited_pages and link_relevance > 0:
                    queue.append(linked)

            if len(document_urls) >= max_documents:
                break

    page_urls.sort(key=lambda url: _page_relevance(query, url, url), reverse=True)
    return page_urls[:10], document_urls[:max_documents]
