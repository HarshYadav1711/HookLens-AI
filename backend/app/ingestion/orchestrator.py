import asyncio
import os

from app.config import get_settings
from app.ingestion.instagram import InstagramIngestStrategy
from app.ingestion.youtube import YouTubeIngestStrategy
from app.models.video import NormalizedVideo
from app.schemas.ingest import IngestResponse
from app.utils.errors import IngestError, UnsupportedUrlError


class IngestOrchestrator:
    """Coordinates dual-video ingestion (YouTube + Instagram)."""

    def __init__(self) -> None:
        self._youtube = YouTubeIngestStrategy()
        self._instagram = InstagramIngestStrategy()

    async def ingest_pair(self, youtube_url: str, instagram_url: str) -> IngestResponse:
        settings = get_settings()
        os.makedirs(settings.data_dir, exist_ok=True)

        youtube_task = asyncio.to_thread(self._youtube.ingest, youtube_url)
        instagram_task = asyncio.to_thread(self._instagram.ingest, instagram_url)

        youtube, instagram = await asyncio.gather(youtube_task, instagram_task)
        return IngestResponse(youtube=youtube, instagram=instagram)


_orchestrator: IngestOrchestrator | None = None


def get_orchestrator() -> IngestOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = IngestOrchestrator()
    return _orchestrator


async def run_ingest(youtube_url: str, instagram_url: str) -> IngestResponse:
    try:
        return await get_orchestrator().ingest_pair(youtube_url, instagram_url)
    except UnsupportedUrlError:
        raise
    except IngestError:
        raise
    except Exception as exc:
        raise IngestError(f"Ingestion failed: {exc}") from exc
