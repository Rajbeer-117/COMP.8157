from __future__ import annotations

import time
from typing import Any, Protocol
from src.schema import SearchResult
from src.evaluation.metrics import recall_at_k, latency_summary

class SearchAdapter(Protocol):
    name: str
    def search(self, query_text: str, top_k: int, filters: dict[str, Any] | None = None) -> list[SearchResult]: ...


def run_benchmark(adapters: list[SearchAdapter], queries: list[dict[str, Any]], ground_truth_adapter: SearchAdapter, repeats: int = 3) -> dict[str, Any]:
    all_results: dict[str, Any] = {"systems": {}}
    for adapter in adapters:
        system_rows = []
        for q in queries:
            gt = ground_truth_adapter.search(q["text"], q.get("top_k", 10), q.get("filters", {}))
            gt_ids = [r.doc_id for r in gt]
            latencies = []
            last_results: list[SearchResult] = []
            for _ in range(repeats):
                start = time.perf_counter()
                last_results = adapter.search(q["text"], q.get("top_k", 10), q.get("filters", {}))
                latencies.append((time.perf_counter() - start) * 1000)
            ids = [r.doc_id for r in last_results]
            row = {
                "query_id": q["query_id"],
                "query_text": q["text"],
                "filters": q.get("filters", {}),
                "latency_ms": latency_summary(latencies),
                "recall_at_10": recall_at_k(ids, gt_ids, 10),
                "retrieved_ids": ids,
                "top_results": [r.model_dump() for r in last_results],
            }
            system_rows.append(row)
        all_results["systems"][adapter.name] = system_rows
    return all_results
