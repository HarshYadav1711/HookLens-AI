import hashlib

import pytest
from qdrant_client import QdrantClient

from app.config import get_settings
from app.retrieval import embeddings, qdrant_store

_EMBED_DIM = 384


def _deterministic_vector(text: str) -> list[float]:
    digest = hashlib.sha256(text.encode()).digest()
    values: list[float] = []
    while len(values) < _EMBED_DIM:
        values.extend(byte / 255.0 for byte in digest)
    return values[:_EMBED_DIM]


@pytest.fixture
def retrieval_env(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("QDRANT_COLLECTION", "test_hooklens_chunks")
    get_settings.cache_clear()

    client = QdrantClient(location=":memory:")
    qdrant_store.set_client(client)
    monkeypatch.setattr(embeddings, "embed_texts", lambda texts: [_deterministic_vector(t) for t in texts])
    monkeypatch.setattr(embeddings, "embed_query", lambda query: _deterministic_vector(query))

    yield tmp_path

    qdrant_store.set_client(None)
    get_settings.cache_clear()
