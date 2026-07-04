from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import argparse
from src.data_pipeline import read_jsonl
from src.db.milvus_adapter import MilvusAdapter

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
args = parser.parse_args()

docs = read_jsonl(args.input)
adapter = MilvusAdapter()
adapter.load_documents(docs)
print(f"Loaded {len(docs)} documents into Milvus.")
