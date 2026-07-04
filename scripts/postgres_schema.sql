CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS cyber_documents (
    doc_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity DOUBLE PRECISION NOT NULL,
    cvss TEXT,
    platform TEXT,
    vendor TEXT,
    published_date DATE,
    tactic TEXT,
    technique TEXT,
    embedding vector(384)
);

CREATE INDEX IF NOT EXISTS idx_cyber_source ON cyber_documents(source);
CREATE INDEX IF NOT EXISTS idx_cyber_platform ON cyber_documents(platform);
CREATE INDEX IF NOT EXISTS idx_cyber_tactic ON cyber_documents(tactic);
CREATE INDEX IF NOT EXISTS idx_cyber_severity ON cyber_documents(severity);
CREATE INDEX IF NOT EXISTS idx_cyber_published_date ON cyber_documents(published_date);

-- HNSW index for cosine distance. Build this after data loading for large datasets.
CREATE INDEX IF NOT EXISTS idx_cyber_embedding_hnsw
ON cyber_documents
USING hnsw (embedding vector_cosine_ops);
