from __future__ import annotations

import re

from backend.config.sources import SOURCES, SourceConfig


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def score_source(query: str, source: SourceConfig) -> float:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return 0.0

    keyword_tokens = set()
    for keyword in source["keywords"]:
        keyword_tokens.update(_tokenize(keyword))

    name_tokens = _tokenize(source["name"])
    domain_tokens = _tokenize(source["domain"].replace(".", " "))

    overlap = query_tokens & (keyword_tokens | name_tokens | domain_tokens)
    score = float(len(overlap))

    type_hints = {
        "market": {"stock", "equity", "report", "annual", "company", "bourse", "masi", "telecom"},
        "macro": {"exchange", "rate", "currency", "monetary", "interest", "dirham", "macro"},
        "statistics": {"gdp", "inflation", "statistics", "employment", "population", "indicator"},
        "regulatory": {"prospectus", "regulatory", "disclosure", "ipo", "bond", "ammc"},
    }
    score += float(len(query_tokens & type_hints.get(source["type"], set()))) * 0.5
    return score


def select_relevant_sources(query: str, min_score: float = 0.5) -> list[SourceConfig]:
    ranked = sorted(
        ((score_source(query, source), source) for source in SOURCES),
        key=lambda item: item[0],
        reverse=True,
    )
    selected = [source for score, source in ranked if score >= min_score]
    if selected:
        return selected[:2]
    return [ranked[0][1]] if ranked else []
