from __future__ import annotations

import statistics
from typing import Iterable


def recall_at_k(retrieved_ids: list[str], ground_truth_ids: list[str], k: int) -> float:
    if not ground_truth_ids:
        return 0.0
    retrieved = set(retrieved_ids[:k])
    truth = set(ground_truth_ids[:k])
    return len(retrieved & truth) / len(truth)


def latency_summary(latencies_ms: Iterable[float]) -> dict[str, float]:
    values = sorted(latencies_ms)
    if not values:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "mean": 0.0}
    def pct(p: float) -> float:
        idx = min(len(values)-1, int(round((p/100) * (len(values)-1))))
        return values[idx]
    return {
        "p50": pct(50),
        "p95": pct(95),
        "p99": pct(99),
        "mean": statistics.mean(values),
    }
