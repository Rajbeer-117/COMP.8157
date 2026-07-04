from __future__ import annotations

import hashlib
import numpy as np
from src.config import settings

class EmbeddingModel:
    """Embedding wrapper.

    For classroom/demo reproducibility, the default is a deterministic hash embedding
    that works offline. Set USE_SENTENCE_TRANSFORMERS=true in .env to use a real
    Sentence-Transformers model.
    """

    def __init__(self, dim: int | None = None):
        self.dim = dim or settings.embedding_dim
        self._model = None
        if settings.use_sentence_transformers:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(settings.embedding_model)
            except Exception as exc:
                print(f"Warning: SentenceTransformer failed; using hash embeddings. Reason: {exc}")
                self._model = None

    def encode(self, texts: list[str]) -> np.ndarray:
        if self._model is not None:
            vectors = self._model.encode(texts, normalize_embeddings=True)
            return np.asarray(vectors, dtype=np.float32)
        return np.vstack([self._hash_embed(t) for t in texts]).astype(np.float32)

    def encode_one(self, text: str) -> list[float]:
        return self.encode([text])[0].tolist()

    def _hash_embed(self, text: str) -> np.ndarray:
        tokens = [t.lower().strip(".,:;()[]{}!?'\"") for t in text.split() if t.strip()]
        vec = np.zeros(self.dim, dtype=np.float32)
        for tok in tokens:
            digest = hashlib.md5(tok.encode("utf-8")).hexdigest()
            idx = int(digest[:8], 16) % self.dim
            sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm
