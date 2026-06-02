import pytest

from app.graph.build import build_comparison_graph
from app.graph.engine import ReasoningEngine
from app.ingestion.normalize import build_normalized_from_metadata
from app.models.video import TranscriptSegment, TranscriptStatus, VideoPlatform
from app.retrieval.indexer import index_session
from app.retrieval.session_store import save_session
from langgraph.checkpoint.memory import MemorySaver


@pytest.fixture
def indexed_session(retrieval_env):

    session_id = "graph-session"
    youtube = build_normalized_from_metadata(
        platform=VideoPlatform.YOUTUBE,
        url="https://youtube.com/watch?v=yt",
        video_id="yt",
        raw={"title": "YT", "view_count": 1000, "like_count": 50, "comment_count": 10},
        metadata_ok=True,
    ).model_copy(
        update={
            "transcript": [
                TranscriptSegment(start_seconds=0, end_seconds=2, text="YouTube watch time hook.")
            ],
            "transcript_status": TranscriptStatus.AVAILABLE,
        }
    )
    instagram = build_normalized_from_metadata(
        platform=VideoPlatform.INSTAGRAM,
        url="https://instagram.com/reel/ig",
        video_id="ig",
        raw={"title": "IG", "view_count": 500, "like_count": 40, "comment_count": 8},
        metadata_ok=True,
    ).model_copy(
        update={
            "transcript": [
                TranscriptSegment(start_seconds=0, end_seconds=2, text="Instagram reel trend hook.")
            ],
            "transcript_status": TranscriptStatus.AVAILABLE,
        }
    )
    save_session(session_id, youtube, instagram)
    index_session(session_id, youtube, instagram)
    return session_id


@pytest.mark.asyncio
async def test_engine_stream_emits_citations_and_tokens(indexed_session, monkeypatch):
    async def fake_stream(system_prompt, user_prompt, history=None):
        yield "Evidence-backed "
        yield "answer [1]."

    monkeypatch.setattr("app.graph.nodes.stream_chat", fake_stream)

    memory = MemorySaver()
    graph = build_comparison_graph().compile(checkpointer=memory)

    import app.graph.engine as engine_module

    async def _fake_get_graph():
        return graph

    monkeypatch.setattr(engine_module, "get_compiled_graph", _fake_get_graph)

    engine = ReasoningEngine()
    events = []
    async for event in engine.stream_turn(
        indexed_session, "Compare hooks", thread_id="t1"
    ):
        events.append(event)

    event_types = [e.event for e in events]
    assert "citations" in event_types
    assert "token" in event_types
    assert "done" in event_types
    citations_event = next(e for e in events if e.event == "citations")
    assert isinstance(citations_event.data, list)
    assert citations_event.data[0]["video_label"] in ("A", "B")

    history = await engine.get_thread_history(indexed_session, thread_id="t1")
    assert len(history) >= 2
    assert history[0].role == "user"
    assert history[1].role == "assistant"
