from __future__ import annotations

from datetime import date
from typing import Any
from pydantic import BaseModel, Field

class CyberDocument(BaseModel):
    doc_id: str
    source: str
    title: str
    description: str
    severity: float = Field(ge=0, le=10)
    cvss: str
    platform: str
    vendor: str
    published_date: date
    tactic: str
    technique: str
    embedding: list[float] | None = None

    @property
    def searchable_text(self) -> str:
        return f"{self.title}. {self.description}. Tactic: {self.tactic}. Platform: {self.platform}."

class HybridQuery(BaseModel):
    query_id: str
    text: str
    top_k: int = 10
    filters: dict[str, Any] = Field(default_factory=dict)

class SearchResult(BaseModel):
    doc_id: str
    score: float
    title: str
    description: str
    metadata: dict[str, Any]
