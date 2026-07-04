from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import argparse
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

with open(args.input, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []
for system, items in data["systems"].items():
    for row in items:
        rows.append({
            "system": system,
            "query_id": row["query_id"],
            "p50_ms": row["latency_ms"]["p50"],
            "p95_ms": row["latency_ms"]["p95"],
            "recall_at_10": row["recall_at_10"],
        })

df = pd.DataFrame(rows)
out = Path(args.output)
out.mkdir(parents=True, exist_ok=True)
df.to_csv(out / "benchmark_summary.csv", index=False)

lat = df.groupby("system")["p95_ms"].mean().sort_values()
plt.figure()
lat.plot(kind="bar")
plt.ylabel("Average P95 latency (ms)")
plt.title("Hybrid Query Latency by System")
plt.tight_layout()
plt.savefig(out / "latency_p95.png", dpi=200)
plt.close()

rec = df.groupby("system")["recall_at_10"].mean().sort_values(ascending=False)
plt.figure()
rec.plot(kind="bar")
plt.ylabel("Average Recall@10")
plt.title("Hybrid Retrieval Recall by System")
plt.ylim(0, 1.05)
plt.tight_layout()
plt.savefig(out / "recall_at_10.png", dpi=200)
plt.close()

print(f"Charts and CSV saved to {out}")
