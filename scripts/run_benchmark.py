from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import argparse
import json
from pathlib import Path
from src.data_pipeline import load_queries, read_jsonl
from src.db.local_adapter import LocalExactAdapter
from src.evaluation.benchmark import run_benchmark

parser = argparse.ArgumentParser()
parser.add_argument("--systems", nargs="+", default=["local"], help="local postgres milvus weaviate")
parser.add_argument("--queries", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--data", default="data/processed_docs.jsonl")
parser.add_argument("--repeats", type=int, default=3)
args = parser.parse_args()

queries = load_queries(args.queries)
docs = read_jsonl(args.data)
ground_truth = LocalExactAdapter(docs)

adapters = []
for name in args.systems:
    if name == "local":
        adapters.append(ground_truth)
    elif name == "postgres":
        from src.db.postgres_adapter import PostgresAdapter
        adapters.append(PostgresAdapter())
    elif name == "milvus":
        from src.db.milvus_adapter import MilvusAdapter
        adapters.append(MilvusAdapter())
    elif name == "weaviate":
        from src.db.weaviate_adapter import WeaviateAdapter
        adapters.append(WeaviateAdapter())
    else:
        raise ValueError(f"Unknown system: {name}")

results = run_benchmark(adapters, queries, ground_truth, repeats=args.repeats)
Path(args.output).parent.mkdir(parents=True, exist_ok=True)
with open(args.output, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"Benchmark saved to {args.output}")
