from pydantic import BaseModel, Field, field_validator

from app.models.video import NormalizedVideo


class IngestRequest(BaseModel):
    youtube_url: str = Field(..., min_length=10, description="Public YouTube video URL")
    instagram_url: str = Field(..., min_length=10, description="Public Instagram Reel URL")

    @field_validator("youtube_url", "instagram_url")
    @classmethod
    def strip_url(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("URL cannot be empty")
        return cleaned


class IngestResponse(BaseModel):
    youtube: NormalizedVideo
    instagram: NormalizedVideo
