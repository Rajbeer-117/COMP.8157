from __future__ import annotations

from typing import Any
import numpy as np
from src.embeddings import EmbeddingModel
from src.schema import CyberDocument, SearchResult


def _passes_filters(doc: CyberDocument, filters: dict[str, Any]) -> bool:
    if not filters:
        return True
    if "platform" in filters and doc.platform.lower() != str(filters["platform"]).lower():
        return False
    if "source" in filters and doc.source.lower() != str(filters["source"]).lower():
        return False
    if "tactic" in filters and doc.tactic.lower() != str(filters["tactic"]).lower():
        return False
    if "min_severity" in filters and doc.severity < float(filters["min_severity"]):
        return False
    if "max_severity" in filters and doc.severity > float(filters["max_severity"]):
        return False
    return True


def exact_search(docs: list[CyberDocument], query_text: str, top_k: int, filters: dict[str, Any] | None = None) -> list[SearchResult]:
    filters = filters or {}
    candidates = [d for d in docs if _passes_filters(d, filters) and d.embedding is not None]
    if not candidates:
        return []
    model = EmbeddingModel(dim=len(candidates[0].embedding or []))
    q = np.asarray(model.encode_one(query_text), dtype=np.float32)
    results: list[SearchResult] = []
    for d in candidates:
        v = np.asarray(d.embedding, dtype=np.float32)
        score = float(np.dot(q, v) / ((np.linalg.norm(q) * np.linalg.norm(v)) or 1.0))
        results.append(SearchResult(
            doc_id=d.doc_id,
            score=score,
            title=d.title,
            description=d.description,
            metadata={
                "source": d.source,
                "severity": d.severity,
                "platform": d.platform,
                "vendor": d.vendor,
                "tactic": d.tactic,
                "technique": d.technique,
                "published_date": str(d.published_date),
            }
        ))
    return sorted(results, key=lambda r: r.score, reverse=True)[:top_k]
