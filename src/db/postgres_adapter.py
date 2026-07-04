from __future__ import annotations

from typing import Any
import psycopg2
from pgvector.psycopg2 import register_vector
from src.config import settings
from src.embeddings import EmbeddingModel
from src.schema import CyberDocument, SearchResult

class PostgresAdapter:
    name = "postgres_pgvector"

    def __init__(self):
        self.conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
        )
        register_vector(self.conn)
        self.model = EmbeddingModel()

    def init_schema(self) -> None:
        with open("scripts/postgres_schema.sql", "r", encoding="utf-8") as f, self.conn.cursor() as cur:
            cur.execute(f.read())
        self.conn.commit()

    def load_documents(self, docs: list[CyberDocument]) -> None:
        sql = """
        INSERT INTO cyber_documents
        (doc_id, source, title, description, severity, cvss, platform, vendor, published_date, tactic, technique, embedding)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (doc_id) DO UPDATE SET
          source=EXCLUDED.source,
          title=EXCLUDED.title,
          description=EXCLUDED.description,
          severity=EXCLUDED.severity,
          cvss=EXCLUDED.cvss,
          platform=EXCLUDED.platform,
          vendor=EXCLUDED.vendor,
          published_date=EXCLUDED.published_date,
          tactic=EXCLUDED.tactic,
          technique=EXCLUDED.technique,
          embedding=EXCLUDED.embedding;
        """
        with self.conn.cursor() as cur:
            for d in docs:
                cur.execute(sql, (d.doc_id, d.source, d.title, d.description, d.severity, d.cvss, d.platform, d.vendor, d.published_date, d.tactic, d.technique, d.embedding))
        self.conn.commit()

    def search(self, query_text: str, top_k: int, filters: dict[str, Any] | None = None) -> list[SearchResult]:
        filters = filters or {}
        qvec = self.model.encode_one(query_text)
        where = []
        params: list[Any] = [qvec]
        if "platform" in filters:
            where.append("LOWER(platform) = LOWER(%s)")
            params.append(filters["platform"])
        if "source" in filters:
            where.append("LOWER(source) = LOWER(%s)")
            params.append(filters["source"])
        if "tactic" in filters:
            where.append("LOWER(tactic) = LOWER(%s)")
            params.append(filters["tactic"])
        if "min_severity" in filters:
            where.append("severity >= %s")
            params.append(float(filters["min_severity"]))
        where_sql = "WHERE " + " AND ".join(where) if where else ""
        params.append(top_k)
        sql = f"""
        SELECT doc_id, title, description, source, severity, platform, vendor, tactic, technique, published_date,
               1 - (embedding <=> %s::vector) AS score
        FROM cyber_documents
        {where_sql}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """
        # qvec is used twice: scoring and ordering
        params2 = [qvec] + params[1:-1] + [qvec, top_k]
        with self.conn.cursor() as cur:
            cur.execute(sql, params2)
            rows = cur.fetchall()
        return [SearchResult(
            doc_id=r[0], score=float(r[10]), title=r[1], description=r[2],
            metadata={"source": r[3], "severity": r[4], "platform": r[5], "vendor": r[6], "tactic": r[7], "technique": r[8], "published_date": str(r[9])}
        ) for r in rows]
