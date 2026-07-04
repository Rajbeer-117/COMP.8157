from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable
from src.schema import CyberDocument
from src.embeddings import EmbeddingModel


def read_jsonl(path: str | Path) -> list[CyberDocument]:
    docs: list[CyberDocument] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                docs.append(CyberDocument.model_validate_json(line))
    return docs


def write_jsonl(path: str | Path, docs: Iterable[CyberDocument]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(doc.model_dump_json() + "\n")


def add_embeddings(docs: list[CyberDocument]) -> list[CyberDocument]:
    model = EmbeddingModel()
    vectors = model.encode([d.searchable_text for d in docs])
    output: list[CyberDocument] = []
    for doc, vec in zip(docs, vectors):
        data = doc.model_dump()
        data["embedding"] = vec.tolist()
        output.append(CyberDocument.model_validate(data))
    return output


def load_queries(path: str | Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
