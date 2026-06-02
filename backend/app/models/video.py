from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class VideoPlatform(str, Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"


class ExtractionStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


class TranscriptStatus(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


class TranscriptSource(str, Enum):
    YOUTUBE_TRANSCRIPT_API = "youtube_transcript_api"
    YOUTUBE_TRANSCRIPT_API_AUTO = "youtube_transcript_api_auto"
    FASTER_WHISPER = "faster_whisper"
    UNAVAILABLE = "unavailable"


class TranscriptSegment(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str


class NormalizedVideo(BaseModel):
    """Canonical internal representation for an ingested video."""

    platform: VideoPlatform
    url: str
    video_id: str

    title: str | None = None
    creator: str | None = None
    upload_date: str | None = None
    duration_seconds: float | None = None

    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    hashtags: list[str] | None = None
    follower_count: int | None = None

    engagement_rate: float | None = None

    transcript: list[TranscriptSegment] = Field(default_factory=list)
    transcript_status: TranscriptStatus = TranscriptStatus.UNAVAILABLE
    transcript_source: TranscriptSource = TranscriptSource.UNAVAILABLE

    metadata_status: ExtractionStatus = ExtractionStatus.FAILED
    raw_metadata: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
