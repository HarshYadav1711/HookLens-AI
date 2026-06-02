"""YouTube transcript extraction via youtube-transcript-api."""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from app.models.video import TranscriptSegment, TranscriptSource, TranscriptStatus
from app.utils.errors import TranscriptExtractionError


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


def fetch_youtube_transcript(video_id: str) -> tuple[list[TranscriptSegment], TranscriptSource, TranscriptStatus]:
    try:
        entries = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["en", "en-US", "en-GB", "en-IN"]
        )
        segments = _entries_to_segments(entries)
        if segments:
            return segments, TranscriptSource.YOUTUBE_TRANSCRIPT_API, TranscriptStatus.AVAILABLE
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        pass
    except Exception as exc:
        raise TranscriptExtractionError(f"YouTube transcript API error: {exc}") from exc

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(["en", "en-US", "en-GB"])
        entries = transcript.fetch()
        segments = _entries_to_segments(entries)
        if segments:
            return segments, TranscriptSource.YOUTUBE_TRANSCRIPT_API_AUTO, TranscriptStatus.AVAILABLE
    except Exception:
        pass

    return [], TranscriptSource.UNAVAILABLE, TranscriptStatus.UNAVAILABLE
