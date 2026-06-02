import os

from app.config import get_settings
from app.ingestion.base import VideoIngestStrategy
from app.ingestion.normalize import build_normalized_from_metadata
from app.ingestion.transcript_whisper import transcribe_audio_file
from app.models.video import (
    ExtractionStatus,
    NormalizedVideo,
    TranscriptSource,
    TranscriptStatus,
    VideoPlatform,
)
from app.services.ytdlp import download_audio, extract_metadata
from app.utils.errors import MetadataExtractionError
from app.utils.urls import validate_instagram_url


class InstagramIngestStrategy(VideoIngestStrategy):
    platform = VideoPlatform.INSTAGRAM

    def ingest(self, url: str) -> NormalizedVideo:
        video_id = validate_instagram_url(url)
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

        segments, source, status = self._transcribe_reel(url, video_id, warnings)
        video.transcript = segments
        video.transcript_source = source
        video.transcript_status = status

        if status == TranscriptStatus.UNAVAILABLE:
            video.warnings.append("Instagram transcript unavailable (Whisper could not produce text)")
            if video.metadata_status != ExtractionStatus.FAILED:
                video.metadata_status = ExtractionStatus.PARTIAL

        return video

    def _transcribe_reel(
        self, url: str, video_id: str, warnings: list[str]
    ) -> tuple[list, TranscriptSource, TranscriptStatus]:
        settings = get_settings()
        audio_dir = os.path.join(settings.data_dir, "audio", "instagram", video_id)
        try:
            audio_path = download_audio(url, audio_dir)
            warnings.append("Transcribed Instagram Reel audio with faster-whisper")
            return transcribe_audio_file(audio_path)
        except Exception as exc:
            warnings.append(f"Instagram audio/transcript extraction failed: {exc}")
            return [], TranscriptSource.UNAVAILABLE, TranscriptStatus.UNAVAILABLE
