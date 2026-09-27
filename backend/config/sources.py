"""Single source of truth for all official data sources."""

from __future__ import annotations

from typing import TypedDict


class SourceConfig(TypedDict):
    id: str
    name: str
    url: str
    type: str
    domain: str
    keywords: list[str]


SOURCES: list[SourceConfig] = [
    {
        "id": "casablanca_bourse",
        "name": "Casablanca Stock Exchange",
        "url": "https://www.casablanca-bourse.com/fr",
        "type": "market",
        "domain": "casablanca-bourse.com",
        "keywords": [
            "stock", "equity", "bourse", "masi", "annual report",
            "financial statements", "maroc telecom", "company", "listed",
        ],
    },
    {
        "id": "bkam",
        "name": "Bank Al-Maghrib",
        "url": "https://www.bkam.ma/",
        "type": "macro",
        "domain": "bkam.ma",
        "keywords": [
            "exchange rate", "monetary", "macro", "interest", "currency",
            "dirham", "policy", "inflation",
        ],
    },
    {
        "id": "hcp",
        "name": "Haut-Commissariat au Plan",
        "url": "https://www.hcp.ma/",
        "type": "statistics",
        "domain": "hcp.ma",
        "keywords": [
            "gdp", "inflation", "statistics", "macroeconomic", "employment",
            "population", "sector", "national accounts",
        ],
    },
    {
        "id": "ammc",
        "name": "AMMC",
        "url": "https://www.ammc.ma/",
        "type": "regulatory",
        "domain": "ammc.ma",
        "keywords": [
            "prospectus", "regulatory", "disclosure", "ipo", "bond",
            "compliance", "issuer",
        ],
    },
]

# PDFs are processed only when users upload them. Source crawling does not expose PDF links.
DOWNLOADABLE_EXTENSIONS = (".xls", ".xlsx", ".csv")


def get_source_by_id(source_id: str) -> SourceConfig | None:
    for source in SOURCES:
        if source["id"] == source_id:
            return source
    return None


def get_all_domains() -> set[str]:
    return {source["domain"] for source in SOURCES}
