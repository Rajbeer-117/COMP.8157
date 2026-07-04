from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import argparse
from src.data_pipeline import read_jsonl, write_jsonl, add_embeddings

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

docs = read_jsonl(args.input)
processed = add_embeddings(docs)
write_jsonl(args.output, processed)
print(f"Prepared {len(processed)} documents -> {args.output}")
