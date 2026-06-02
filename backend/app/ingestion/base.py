from abc import ABC, abstractmethod

from app.models.video import NormalizedVideo, VideoPlatform


class VideoIngestStrategy(ABC):
    """Pluggable per-platform ingestion strategy."""

    platform: VideoPlatform

    @abstractmethod
    def ingest(self, url: str) -> NormalizedVideo:
        """Extract metadata and transcript for a single video URL."""
