from __future__ import annotations

from typing import Any
import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import Filter
from src.config import settings
from src.embeddings import EmbeddingModel
from src.schema import CyberDocument, SearchResult

COLLECTION_NAME = "CyberDocument"

class WeaviateAdapter:
    name = "weaviate"

    def __init__(self):
        self.client = weaviate.connect_to_local(host=settings.weaviate_url.replace("http://", "").replace("https://", "").split(":")[0], port=8080)
        self.model = EmbeddingModel()

    def init_collection(self) -> None:
        if self.client.collections.exists(COLLECTION_NAME):
            return
        self.client.collections.create(
            COLLECTION_NAME,
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="doc_id", data_type=DataType.TEXT),
                Property(name="title", data_type=DataType.TEXT),
                Property(name="description", data_type=DataType.TEXT),
                Property(name="source", data_type=DataType.TEXT),
                Property(name="platform", data_type=DataType.TEXT),
                Property(name="vendor", data_type=DataType.TEXT),
                Property(name="tactic", data_type=DataType.TEXT),
                Property(name="technique", data_type=DataType.TEXT),
                Property(name="published_date", data_type=DataType.TEXT),
                Property(name="severity", data_type=DataType.NUMBER),
            ],
        )

    def load_documents(self, docs: list[CyberDocument]) -> None:
        self.init_collection()
        col = self.client.collections.get(COLLECTION_NAME)
        with col.batch.dynamic() as batch:
            for d in docs:
                batch.add_object(
                    properties={
                        "doc_id": d.doc_id,
                        "title": d.title,
                        "description": d.description,
                        "source": d.source,
                        "platform": d.platform,
                        "vendor": d.vendor,
                        "tactic": d.tactic,
                        "technique": d.technique,
                        "published_date": str(d.published_date),
                        "severity": d.severity,
                    },
                    vector=d.embedding,
                )

    def _where_filter(self, filters: dict[str, Any]):
        conditions = []
        if "platform" in filters:
            conditions.append(Filter.by_property("platform").equal(str(filters["platform"])))
        if "source" in filters:
            conditions.append(Filter.by_property("source").equal(str(filters["source"])))
        if "tactic" in filters:
            conditions.append(Filter.by_property("tactic").equal(str(filters["tactic"])))
        if "min_severity" in filters:
            conditions.append(Filter.by_property("severity").greater_or_equal(float(filters["min_severity"])))
        if not conditions:
            return None
        combined = conditions[0]
        for cond in conditions[1:]:
            combined = combined & cond
        return combined

    def search(self, query_text: str, top_k: int, filters: dict[str, Any] | None = None) -> list[SearchResult]:
        filters = filters or {}
        col = self.client.collections.get(COLLECTION_NAME)
        qvec = self.model.encode_one(query_text)
        response = col.query.near_vector(
            near_vector=qvec,
            limit=top_k,
            filters=self._where_filter(filters),
            return_metadata=["distance", "certainty"],
        )
        results = []
        for obj in response.objects:
            p = obj.properties
            score = 1.0 - float(obj.metadata.distance or 0.0)
            results.append(SearchResult(
                doc_id=p.get("doc_id"),
                score=score,
                title=p.get("title", ""),
                description=p.get("description", ""),
                metadata={k: p.get(k) for k in ["source", "severity", "platform", "vendor", "tactic", "technique", "published_date"]},
            ))
        return results
