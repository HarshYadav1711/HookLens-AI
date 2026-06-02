from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    ollama: bool | None = None
