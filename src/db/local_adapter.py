from __future__ import annotations

from typing import Any
from src.schema import CyberDocument, SearchResult
from src.evaluation.local_exact import exact_search

class LocalExactAdapter:
    name = "local_exact"

    def __init__(self, docs: list[CyberDocument]):
        self.docs = docs

    def search(self, query_text: str, top_k: int, filters: dict[str, Any] | None = None) -> list[SearchResult]:
        return exact_search(self.docs, query_text, top_k, filters or {})
