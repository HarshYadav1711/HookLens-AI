import os

from app.config import get_settings
from app.ingestion.base import VideoIngestStrategy
from app.ingestion.normalize import build_normalized_from_metadata
from app.ingestion.transcript_whisper import transcribe_audio_file
from app.ingestion.transcript_youtube import fetch_youtube_transcript
from app.models.video import (
    ExtractionStatus,
    NormalizedVideo,
    TranscriptSource,
    TranscriptStatus,
    VideoPlatform,
)
from app.services.ytdlp import download_audio, extract_metadata
from app.utils.errors import MetadataExtractionError, UnsupportedUrlError
from app.utils.urls import extract_youtube_id, validate_youtube_url


class YouTubeIngestStrategy(VideoIngestStrategy):
    platform = VideoPlatform.YOUTUBE

    def ingest(self, url: str) -> NormalizedVideo:
        video_id = validate_youtube_url(url)
        raw: dict | None = None
        metadata_ok = False
        warnings: list[str] = []

        try:
            raw = extract_metadata(url)
            metadata_ok = True
        except MetadataExtractionError as exc:
            warnings.append(str(exc.message))

        video = build_normalized_from_metadata(
            platform=self.platform,
            url=url,
            video_id=video_id,
            raw=raw,
            metadata_ok=metadata_ok,
        )
        video.warnings.extend(warnings)

        segments, source, status = fetch_youtube_transcript(video_id)

        if not segments:
            segments, source, status = self._whisper_fallback(url, video_id, video.warnings)

        video.transcript = segments
        video.transcript_source = source
        video.transcript_status = status

        if status == TranscriptStatus.UNAVAILABLE:
            video.warnings.append("Transcript unavailable after all extraction strategies")
            if video.metadata_status != ExtractionStatus.FAILED:
                video.metadata_status = ExtractionStatus.PARTIAL

        return video

    def _whisper_fallback(
        self, url: str, video_id: str, warnings: list[str]
    ) -> tuple[list, TranscriptSource, TranscriptStatus]:
        settings = get_settings()
        audio_dir = os.path.join(settings.data_dir, "audio", "youtube", video_id)
        try:
            audio_path = download_audio(url, audio_dir)
            warnings.append("Used faster-whisper fallback for YouTube transcript")
            return transcribe_audio_file(audio_path)
        except Exception as exc:
            warnings.append(f"Whisper fallback failed: {exc}")
            return [], TranscriptSource.UNAVAILABLE, TranscriptStatus.UNAVAILABLE
