"""Qdrant vector store: vectors from chunk text; structured metadata in payload only."""

import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config import get_settings
from app.models.chunk import TranscriptChunk, VideoLabel
from app.retrieval import embeddings

_client: QdrantClient | None = None
_client_override: QdrantClient | None = None


def set_client(client: QdrantClient | None) -> None:
    """Override client (e.g. :memory: for tests)."""
    global _client_override
    _client_override = client


def get_client() -> QdrantClient:
    if _client_override is not None:
        return _client_override
    global _client
    if _client is None:
        settings = get_settings()
        _client = QdrantClient(url=settings.qdrant_url)
    return _client


def _point_id(session_id: str, chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{session_id}:{chunk_id}"))


def _chunk_payload(chunk: TranscriptChunk) -> dict[str, Any]:
    return {
        "session_id": chunk.session_id,
        "video_label": chunk.video_label,
        "video_id": chunk.video_id,
        "chunk_id": chunk.chunk_id,
        "chunk_index": chunk.chunk_index,
        "start_time": chunk.start_time,
        "end_time": chunk.end_time,
        "text": chunk.text,
        "platform": chunk.source.platform.value,
        "url": chunk.source.url,
        "title": chunk.source.title,
        "creator": chunk.source.creator,
        "transcript_source": chunk.source.transcript_source,
    }


def ensure_collection(vector_size: int) -> None:
    settings = get_settings()
    client = get_client()
    names = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in names:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def delete_session_points(session_id: str) -> None:
    settings = get_settings()
    client = get_client()
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=Filter(
            must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))]
        ),
    )


def upsert_chunks(chunks: list[TranscriptChunk]) -> int:
    if not chunks:
        return 0
    texts = [c.text for c in chunks]
    vectors = embeddings.embed_texts(texts)
    ensure_collection(len(vectors[0]))
    settings = get_settings()
    client = get_client()
    points = [
        PointStruct(
            id=_point_id(chunk.session_id, chunk.chunk_id),
            vector=vector,
            payload=_chunk_payload(chunk),
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)
    return len(points)


def search(
    session_id: str,
    query_vector: list[float],
    *,
    top_k: int,
    video_label: VideoLabel | None = None,
    video_id: str | None = None,
) -> list[dict[str, Any]]:
    settings = get_settings()
    client = get_client()
    must: list[FieldCondition] = [
        FieldCondition(key="session_id", match=MatchValue(value=session_id))
    ]
    if video_label is not None:
        must.append(FieldCondition(key="video_label", match=MatchValue(value=video_label)))
    if video_id is not None:
        must.append(FieldCondition(key="video_id", match=MatchValue(value=video_id)))

    response = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        query_filter=Filter(must=must),
        limit=top_k,
        with_payload=True,
    )
    hits: list[dict[str, Any]] = []
    for point in response.points:
        payload = dict(point.payload or {})
        payload["score"] = point.score
        hits.append(payload)
    return hits
