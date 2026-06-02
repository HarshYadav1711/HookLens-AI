"""LangGraph nodes: retrieval, reasoning, citations, generation, memory."""

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.config import get_stream_writer

from app.graph.citations import assemble_citations, build_prompts
from app.graph.reasoning import build_comparison_facts
from app.graph.state import ComparisonState
from app.retrieval.retriever import retrieve
from app.retrieval.session_store import load_session
from app.services.ollama import stream_chat


def _history_from_messages(messages: list) -> list[dict[str, str]]:
    history: list[dict[str, str]] = []
    for msg in messages or []:
        role = getattr(msg, "type", None) or getattr(msg, "role", None)
        content = getattr(msg, "content", None)
        if not content:
            continue
        if role in ("human", "user"):
            history.append({"role": "user", "content": str(content)})
        elif role in ("ai", "assistant"):
            history.append({"role": "assistant", "content": str(content)})
    return history


def retrieve_node(state: ComparisonState) -> ComparisonState:
    session_id = state["session_id"]
    record = load_session(session_id)
    writer = get_stream_writer()

    if record is None:
        msg = "Session not found. Run ingest first."
        writer({"event": "error", "data": {"message": msg}})
        return {"error": msg, "assistant_reply": msg, "citations": []}

    if not record.indexed_fingerprint:
        msg = "Session is not indexed. Call POST /api/sessions/{session_id}/index before chatting."
        writer({"event": "error", "data": {"message": msg}})
        writer({"event": "citations", "data": []})
        writer({"event": "done", "data": {"content": msg}})
        return {"error": msg, "assistant_reply": msg, "citations": []}

    result = retrieve(session_id, state["user_message"])
    return {
        "retrieval_hits": [h.model_dump() for h in result.hits],
        "error": None,
    }


def reasoning_node(state: ComparisonState) -> ComparisonState:
    if state.get("error"):
        return {}
    record = load_session(state["session_id"])
    if record is None:
        return {"error": "Session not found."}
    return {"comparison_facts": build_comparison_facts(record)}


def citation_assembly_node(state: ComparisonState) -> ComparisonState:
    if state.get("error"):
        return {}
    from app.retrieval.retriever import RetrievalHit

    hits = [RetrievalHit(**h) for h in state.get("retrieval_hits", [])]
    citations, evidence_block = assemble_citations(hits)
    system_prompt, user_prompt = build_prompts(
        state.get("comparison_facts", ""),
        evidence_block,
        state["user_message"],
    )
    writer = get_stream_writer()
    writer({"event": "citations", "data": citations})
    return {
        "citations": citations,
        "evidence_block": evidence_block,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }


async def generate_node(state: ComparisonState) -> ComparisonState:
    if state.get("error"):
        writer = get_stream_writer()
        writer({"event": "error", "data": {"message": state["error"]}})
        return {"assistant_reply": f"I cannot answer: {state['error']}"}

    writer = get_stream_writer()
    history = _history_from_messages(state.get("messages", []))
    parts: list[str] = []
    async for token in stream_chat(
        state["system_prompt"],
        state["user_prompt"],
        history=history,
    ):
        parts.append(token)
        writer({"event": "token", "data": {"text": token}})

    reply = "".join(parts)
    writer({"event": "done", "data": {"content": reply}})
    return {"assistant_reply": reply}


def memory_update_node(state: ComparisonState) -> ComparisonState:
    reply = state.get("assistant_reply") or state.get("error")
    if not reply:
        return {}
    return {
        "messages": [
            HumanMessage(content=state["user_message"]),
            AIMessage(content=reply),
        ]
    }


def route_after_retrieve(state: ComparisonState) -> str:
    if state.get("error"):
        return "memory_update"
    return "reasoning"
