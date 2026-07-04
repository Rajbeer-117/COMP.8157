from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "threatintel")
    postgres_user: str = os.getenv("POSTGRES_USER", "threatuser")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "threatpass")

    milvus_host: str = os.getenv("MILVUS_HOST", "localhost")
    milvus_port: str = os.getenv("MILVUS_PORT", "19530")

    weaviate_url: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")

    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "384"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    use_sentence_transformers: bool = os.getenv("USE_SENTENCE_TRANSFORMERS", "false").lower() == "true"

settings = Settings()
