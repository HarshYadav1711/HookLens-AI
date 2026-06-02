from typing import Literal

from pydantic import BaseModel, Field

from app.models.video import VideoPlatform

VideoLabel = Literal["A", "B"]


class ChunkSourceMeta(BaseModel):
    """Lightweight citation fields stored on each chunk payload (not embedded)."""

    platform: VideoPlatform
    url: str
    title: str | None = None
    creator: str | None = None
    transcript_source: str | None = None


class TranscriptChunk(BaseModel):
    chunk_id: str
    session_id: str
    video_label: VideoLabel
    video_id: str
    chunk_index: int
    start_time: float
    end_time: float
    text: str
    source: ChunkSourceMeta
