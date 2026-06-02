from fastapi import APIRouter, HTTPException

from app.ingestion.orchestrator import run_ingest
from app.schemas.health import HealthResponse
from app.schemas.ingest import IngestRequest, IngestResponse
from app.utils.errors import IngestError, UnsupportedUrlError

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="hooklens-api")


@router.post("/ingest", response_model=IngestResponse)
async def ingest_videos(body: IngestRequest) -> IngestResponse:
    try:
        return await run_ingest(body.youtube_url, body.instagram_url)
    except UnsupportedUrlError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    except IngestError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc
