from fastapi import APIRouter, HTTPException

from app.ingestion.orchestrator import run_ingest
from app.retrieval.indexer import index_from_stored_session
from app.retrieval.retriever import retrieve
from app.retrieval.session_store import load_session
from app.schemas.health import HealthResponse
from app.schemas.ingest import IngestRequest, IngestResponse
from app.schemas.retrieval import IndexSessionResponse, RetrieveRequest, RetrieveResponse
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


@router.post("/sessions/{session_id}/index", response_model=IndexSessionResponse)
async def index_session(session_id: str, force: bool = False) -> IndexSessionResponse:
    if load_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        return index_from_stored_session(session_id, force=force)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {exc}") from exc


@router.post("/sessions/{session_id}/retrieve", response_model=RetrieveResponse)
async def retrieve_chunks(session_id: str, body: RetrieveRequest) -> RetrieveResponse:
    try:
        return retrieve(
            session_id,
            body.query,
            video_label=body.video_label,
            video_id=body.video_id,
            top_k=body.top_k,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}") from exc
