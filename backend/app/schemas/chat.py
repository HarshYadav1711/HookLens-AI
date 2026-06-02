from typing import Any

from pydantic import BaseModel, Field

from app.graph.engine import ChatTurnResult, ThreadMessage


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    thread_id: str = Field(default="default", min_length=1)


class ChatResponse(ChatTurnResult):
    pass


class ThreadHistoryResponse(BaseModel):
    session_id: str
    thread_id: str
    messages: list[ThreadMessage]


class StreamEventSchema(BaseModel):
    event: str
    data: Any
