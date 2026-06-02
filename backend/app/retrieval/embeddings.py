"""Sentence-transformers embedding service (encode text only; metadata stays in Qdrant payload)."""

from functools import lru_cache

import numpy as np

from app.config import get_settings


@lru_cache
def _load_model():
    from sentence_transformers import SentenceTransformer

    settings = get_settings()
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _load_model()
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    if isinstance(vectors, np.ndarray) and vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
    return [v.tolist() for v in vectors]


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
