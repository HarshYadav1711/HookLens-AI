from pydantic import BaseModel, Field

from app.models.chunk import VideoLabel
from app.retrieval.indexer import IndexResult
from app.retrieval.retriever import RetrievalResult


class IndexSessionResponse(IndexResult):
    pass


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1)
    video_label: VideoLabel | None = Field(
        default=None, description="Filter to video A (YouTube) or B (Instagram)"
    )
    video_id: str | None = Field(default=None, description="Filter to a specific platform video_id")
    top_k: int | None = Field(default=None, ge=1, le=50)


class RetrieveResponse(RetrievalResult):
    pass
