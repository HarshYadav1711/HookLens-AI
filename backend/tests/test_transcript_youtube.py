from unittest.mock import MagicMock, patch

from app.ingestion.transcript_youtube import fetch_youtube_transcript
from app.models.video import TranscriptSource, TranscriptStatus


def test_fetch_youtube_transcript_uses_instance_api():
    mock_fetched = MagicMock()
    mock_fetched.is_generated = False
    mock_fetched.to_raw_data.return_value = [
        {"text": "Hello hook", "start": 0.0, "duration": 2.0},
    ]

    with patch("app.ingestion.transcript_youtube.YouTubeTranscriptApi") as api_cls:
        api = api_cls.return_value
        api.fetch.return_value = mock_fetched

        segments, source, status = fetch_youtube_transcript("abc123")

    api.fetch.assert_called_once()
    assert len(segments) == 1
    assert segments[0].text == "Hello hook"
    assert source == TranscriptSource.YOUTUBE_TRANSCRIPT_API
    assert status == TranscriptStatus.AVAILABLE
