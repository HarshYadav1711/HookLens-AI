"""Query-time retrieval: embed query only; vectors for transcripts indexed once."""

from pydantic import BaseModel, Field

from app.config import get_settings
from app.models.chunk import VideoLabel
from app.retrieval import embeddings
from app.retrieval import qdrant_store as qdrant
from app.retrieval.session_store import load_session


class RetrievalHit(BaseModel):
    session_id: str
    video_label: VideoLabel
    video_id: str
    chunk_id: str
    chunk_index: int
    start_time: float
    end_time: float
    text: str
    platform: str
    url: str
    title: str | None = None
    creator: str | None = None
    transcript_source: str | None = None
    score: float


class RetrievalResult(BaseModel):
    session_id: str
    query: str
    hits: list[RetrievalHit] = Field(default_factory=list)


def retrieve(
    session_id: str,
    query: str,
    *,
    video_label: VideoLabel | None = None,
    video_id: str | None = None,
    top_k: int | None = None,
) -> RetrievalResult:
    if load_session(session_id) is None:
        raise FileNotFoundError(f"Session not found: {session_id}")

    settings = get_settings()
    k = top_k or settings.retrieval_top_k
    vector = embeddings.embed_query(query.strip())
    raw_hits = qdrant.search(
        session_id,
        vector,
        top_k=k,
        video_label=video_label,
        video_id=video_id,
    )

    hits = [
        RetrievalHit(
            session_id=session_id,
            video_label=h["video_label"],
            video_id=h["video_id"],
            chunk_id=h["chunk_id"],
            chunk_index=h["chunk_index"],
            start_time=h["start_time"],
            end_time=h["end_time"],
            text=h["text"],
            platform=h["platform"],
            url=h["url"],
            title=h.get("title"),
            creator=h.get("creator"),
            transcript_source=h.get("transcript_source"),
            score=float(h["score"]),
        )
        for h in raw_hits
    ]
    return RetrievalResult(session_id=session_id, query=query, hits=hits)
