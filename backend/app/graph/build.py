"""Compile the HookLens comparison LangGraph."""

import os

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, StateGraph

from app.config import get_settings
from app.graph.nodes import (
    citation_assembly_node,
    generate_node,
    memory_update_node,
    reasoning_node,
    retrieve_node,
    route_after_retrieve,
)
from app.graph.state import ComparisonState

_compiled_graph = None
_checkpointer: AsyncSqliteSaver | None = None


async def get_checkpointer() -> AsyncSqliteSaver:
    global _checkpointer
    if _checkpointer is None:
        settings = get_settings()
        os.makedirs(settings.data_dir, exist_ok=True)
        _checkpointer = AsyncSqliteSaver.from_conn_string(settings.checkpoint_db_path)
        await _checkpointer.setup()
    return _checkpointer


def build_comparison_graph():
    graph = StateGraph(ComparisonState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("citation_assembly", citation_assembly_node)
    graph.add_node("generate", generate_node)
    graph.add_node("memory_update", memory_update_node)

    graph.set_entry_point("retrieve")
    graph.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {"reasoning": "reasoning", "memory_update": "memory_update"},
    )
    graph.add_edge("reasoning", "citation_assembly")
    graph.add_edge("citation_assembly", "generate")
    graph.add_edge("generate", "memory_update")
    graph.add_edge("memory_update", END)

    return graph


async def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        checkpointer = await get_checkpointer()
        _compiled_graph = build_comparison_graph().compile(checkpointer=checkpointer)
    return _compiled_graph
