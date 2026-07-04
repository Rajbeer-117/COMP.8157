from __future__ import annotations

from typing import Any
from pymilvus import DataType, MilvusClient
from src.config import settings
from src.embeddings import EmbeddingModel
from src.schema import CyberDocument, SearchResult

COLLECTION_NAME = "cyber_documents"

class MilvusAdapter:
    name = "milvus"

    def __init__(self):
        self.client = MilvusClient(uri=f"http://{settings.milvus_host}:{settings.milvus_port}")
        self.model = EmbeddingModel()

    def init_collection(self, dim: int = 384) -> None:
        if self.client.has_collection(COLLECTION_NAME):
            return
        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field("doc_id", DataType.VARCHAR, is_primary=True, max_length=128)
        schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=dim)
        schema.add_field("title", DataType.VARCHAR, max_length=512)
        schema.add_field("description", DataType.VARCHAR, max_length=4096)
        schema.add_field("source", DataType.VARCHAR, max_length=64)
        schema.add_field("platform", DataType.VARCHAR, max_length=64)
        schema.add_field("vendor", DataType.VARCHAR, max_length=128)
        schema.add_field("tactic", DataType.VARCHAR, max_length=128)
        schema.add_field("technique", DataType.VARCHAR, max_length=64)
        schema.add_field("severity", DataType.DOUBLE)
        schema.add_field("published_date", DataType.VARCHAR, max_length=32)
        index_params = self.client.prepare_index_params()
        index_params.add_index("embedding", index_type="HNSW", metric_type="COSINE", params={"M": 16, "efConstruction": 200})
        self.client.create_collection(COLLECTION_NAME, schema=schema, index_params=index_params)

    def load_documents(self, docs: list[CyberDocument]) -> None:
        self.init_collection(dim=len(docs[0].embedding or []))
        rows = []
        for d in docs:
            rows.append({
                "doc_id": d.doc_id,
                "embedding": d.embedding,
                "title": d.title,
                "description": d.description,
                "source": d.source,
                "platform": d.platform,
                "vendor": d.vendor,
                "tactic": d.tactic,
                "technique": d.technique,
                "severity": d.severity,
                "published_date": str(d.published_date),
            })
        self.client.upsert(collection_name=COLLECTION_NAME, data=rows)

    def _filter_expr(self, filters: dict[str, Any]) -> str:
        parts = []
        if "platform" in filters:
            parts.append(f'platform == "{filters["platform"]}"')
        if "source" in filters:
            parts.append(f'source == "{filters["source"]}"')
        if "tactic" in filters:
            parts.append(f'tactic == "{filters["tactic"]}"')
        if "min_severity" in filters:
            parts.append(f'severity >= {float(filters["min_severity"])}')
        return " and ".join(parts)

    def search(self, query_text: str, top_k: int, filters: dict[str, Any] | None = None) -> list[SearchResult]:
        filters = filters or {}
        qvec = self.model.encode_one(query_text)
        res = self.client.search(
            collection_name=COLLECTION_NAME,
            data=[qvec],
            limit=top_k,
            filter=self._filter_expr(filters) or None,
            output_fields=["doc_id", "title", "description", "source", "severity", "platform", "vendor", "tactic", "technique", "published_date"],
            search_params={"metric_type": "COSINE", "params": {"ef": 64}},
        )
        results = []
        for hit in res[0]:
            entity = hit.get("entity", {})
            results.append(SearchResult(
                doc_id=entity.get("doc_id"),
                score=float(hit.get("distance", 0.0)),
                title=entity.get("title", ""),
                description=entity.get("description", ""),
                metadata={k: entity.get(k) for k in ["source", "severity", "platform", "vendor", "tactic", "technique", "published_date"]},
            ))
        return results
