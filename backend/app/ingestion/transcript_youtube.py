"""YouTube transcript extraction via youtube-transcript-api."""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from app.models.video import TranscriptSegment, TranscriptSource, TranscriptStatus

_PREFERRED_LANGUAGES = ["en", "en-US", "en-GB", "en-IN"]


def _entries_to_segments(entries: list[dict]) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []
    for item in entries:
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        start = float(item.get("start", 0))
        duration = float(item.get("duration", 0))
        segments.append(
            TranscriptSegment(
                start_seconds=start,
                end_seconds=start + duration,
                text=text,
            )
        )
    return segments


def _segments_from_fetched(fetched) -> list[TranscriptSegment]:
    if hasattr(fetched, "to_raw_data"):
        return _entries_to_segments(fetched.to_raw_data())
    return _entries_to_segments(list(fetched))


def fetch_youtube_transcript(video_id: str) -> tuple[list[TranscriptSegment], TranscriptSource, TranscriptStatus]:
    """Fetch captions via youtube-transcript-api v1.x instance API."""
    api = YouTubeTranscriptApi()

    try:
        fetched = api.fetch(video_id, languages=_PREFERRED_LANGUAGES)
        segments = _segments_from_fetched(fetched)
        if segments:
            source = (
                TranscriptSource.YOUTUBE_TRANSCRIPT_API_AUTO
                if fetched.is_generated
                else TranscriptSource.YOUTUBE_TRANSCRIPT_API
            )
            return segments, source, TranscriptStatus.AVAILABLE
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        pass
    except Exception:
        pass

    try:
        transcript = api.list(video_id).find_generated_transcript(_PREFERRED_LANGUAGES)
        fetched = transcript.fetch()
        segments = _segments_from_fetched(fetched)
        if segments:
            return segments, TranscriptSource.YOUTUBE_TRANSCRIPT_API_AUTO, TranscriptStatus.AVAILABLE
    except Exception:
        pass

    return [], TranscriptSource.UNAVAILABLE, TranscriptStatus.UNAVAILABLE
