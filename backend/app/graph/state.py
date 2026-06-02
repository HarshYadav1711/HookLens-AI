"""LangGraph state for creator comparison Q&A."""

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class ComparisonState(TypedDict, total=False):
    session_id: str
    thread_id: str
    user_message: str

    messages: Annotated[list[Any], add_messages]

    retrieval_hits: list[dict[str, Any]]
    comparison_facts: str
    evidence_block: str
    citations: list[dict[str, Any]]

    system_prompt: str
    user_prompt: str
    assistant_reply: str

    error: str | None
