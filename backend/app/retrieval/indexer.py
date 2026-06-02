"""Index transcript chunks once per session; skip re-embedding when fingerprint unchanged."""

from pydantic import BaseModel

from app.config import get_settings
from app.models.video import NormalizedVideo
from app.retrieval.chunking import chunk_session_pair
from app.retrieval import qdrant_store as qdrant
from app.retrieval.session_store import (
    load_session,
    mark_indexed,
    save_session,
    transcript_fingerprint,
)


class IndexResult(BaseModel):
    session_id: str
    chunks_indexed: int
    skipped_reindex: bool
    fingerprint: str


def index_session(
    session_id: str,
    video_a: NormalizedVideo,
    video_b: NormalizedVideo,
    *,
    force: bool = False,
) -> IndexResult:
    settings = get_settings()
    fingerprint = transcript_fingerprint(video_a, video_b)

    existing = load_session(session_id)
    if existing is None:
        save_session(session_id, video_a, video_b)
        existing = load_session(session_id)
    assert existing is not None

    if (
        not force
        and existing.indexed_fingerprint == fingerprint
        and existing.indexed_fingerprint is not None
    ):
        return IndexResult(
            session_id=session_id,
            chunks_indexed=0,
            skipped_reindex=True,
            fingerprint=fingerprint,
        )

    chunks = chunk_session_pair(
        session_id,
        video_a,
        video_b,
        max_chars=settings.chunk_max_chars,
        overlap_chars=settings.chunk_overlap_chars,
    )

    if existing.indexed_fingerprint and existing.indexed_fingerprint != fingerprint:
        qdrant.delete_session_points(session_id)

    indexed_count = qdrant.upsert_chunks(chunks)
    mark_indexed(session_id, fingerprint)

    return IndexResult(
        session_id=session_id,
        chunks_indexed=indexed_count,
        skipped_reindex=False,
        fingerprint=fingerprint,
    )


def index_from_stored_session(session_id: str, *, force: bool = False) -> IndexResult:
    record = load_session(session_id)
    if not record:
        raise FileNotFoundError(f"Session not found: {session_id}")
    return index_session(session_id, record.video_a, record.video_b, force=force)
