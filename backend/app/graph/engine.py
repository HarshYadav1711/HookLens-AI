"""
Public reasoning engine interface for the UI and API layer.

Streams LangGraph custom events (citations, tokens, done) and persists
conversation turns via SQLite checkpointing.
"""

import json
from collections.abc import AsyncIterator
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field

from app.graph.build import get_compiled_graph
from app.graph.state import ComparisonState
from app.retrieval.session_store import load_session

StreamEventType = Literal["citations", "token", "done", "error"]


class StreamEvent(BaseModel):
    event: StreamEventType
    data: dict[str, Any] | list[Any] | str = Field(default_factory=dict)


class ChatTurnResult(BaseModel):
    session_id: str
    thread_id: str
    assistant_reply: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None


class ThreadMessage(BaseModel):
    role: str
    content: str


class ReasoningEngine:
    """Stateful comparison Q&A powered by LangGraph."""

    def _thread_config(self, session_id: str, thread_id: str) -> dict:
        return {"configurable": {"thread_id": f"{session_id}:{thread_id}"}}

    def _validate_session(self, session_id: str) -> None:
        if load_session(session_id) is None:
            raise FileNotFoundError(f"Session not found: {session_id}")

    async def stream_turn(
        self,
        session_id: str,
        message: str,
        *,
        thread_id: str = "default",
    ) -> AsyncIterator[StreamEvent]:
        """
        Run one conversation turn with streaming output.

        Yields StreamEvent objects suitable for SSE/WebSocket forwarding.
        """
        self._validate_session(session_id)
        graph = await get_compiled_graph()
        config = self._thread_config(session_id, thread_id)

        initial: ComparisonState = {
            "session_id": session_id,
            "thread_id": thread_id,
            "user_message": message.strip(),
        }

        async for chunk in graph.astream(
            initial,
            config=config,
            stream_mode="custom",
        ):
            if isinstance(chunk, dict):
                event_type = chunk.get("event")
                data = chunk.get("data")
                if event_type in ("citations", "token", "done", "error"):
                    yield StreamEvent(event=event_type, data=data)  # type: ignore[arg-type]

    async def run_turn(
        self,
        session_id: str,
        message: str,
        *,
        thread_id: str = "default",
    ) -> ChatTurnResult:
        """Non-streaming turn: aggregates stream events into a final result."""
        citations: list[dict[str, Any]] = []
        tokens: list[str] = []
        error: str | None = None

        async for event in self.stream_turn(session_id, message, thread_id=thread_id):
            if event.event == "citations" and isinstance(event.data, list):
                citations = event.data
            elif event.event == "token" and isinstance(event.data, dict):
                tokens.append(event.data.get("text", ""))
            elif event.event == "done" and isinstance(event.data, dict):
                pass
            elif event.event == "error" and isinstance(event.data, dict):
                error = event.data.get("message")

        reply = "".join(tokens)
        if not reply and error:
            reply = f"I cannot answer: {error}"

        return ChatTurnResult(
            session_id=session_id,
            thread_id=thread_id,
            assistant_reply=reply,
            citations=citations,
            error=error,
        )

    async def get_thread_history(
        self,
        session_id: str,
        *,
        thread_id: str = "default",
    ) -> list[ThreadMessage]:
        """Return prior turns from LangGraph checkpoint state."""
        self._validate_session(session_id)
        graph = await get_compiled_graph()
        config = self._thread_config(session_id, thread_id)
        snapshot = await graph.aget_state(config)
        if not snapshot or not snapshot.values:
            return []

        messages = snapshot.values.get("messages", [])
        out: list[ThreadMessage] = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                out.append(ThreadMessage(role="user", content=str(msg.content)))
            elif isinstance(msg, AIMessage):
                out.append(ThreadMessage(role="assistant", content=str(msg.content)))
        return out


_engine: ReasoningEngine | None = None


def get_reasoning_engine() -> ReasoningEngine:
    global _engine
    if _engine is None:
        _engine = ReasoningEngine()
    return _engine
