"""Compile the HookLens comparison LangGraph."""

import os
from contextlib import AsyncExitStack

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

_exit_stack: AsyncExitStack | None = None
_checkpointer: AsyncSqliteSaver | None = None
_compiled_graph = None


async def start_graph_runtime() -> None:
    """Open the SQLite checkpointer and compile the graph for app lifetime."""
    global _exit_stack, _checkpointer, _compiled_graph
    if _checkpointer is not None:
        return

    settings = get_settings()
    os.makedirs(settings.data_dir, exist_ok=True)

    _exit_stack = AsyncExitStack()
    _checkpointer = await _exit_stack.enter_async_context(
        AsyncSqliteSaver.from_conn_string(settings.checkpoint_db_path)
    )
    await _checkpointer.setup()
    _compiled_graph = build_comparison_graph().compile(checkpointer=_checkpointer)


async def stop_graph_runtime() -> None:
    """Release checkpointer resources on app shutdown."""
    global _exit_stack, _checkpointer, _compiled_graph
    if _exit_stack is not None:
        await _exit_stack.aclose()
    _exit_stack = None
    _checkpointer = None
    _compiled_graph = None


async def get_checkpointer() -> AsyncSqliteSaver:
    if _checkpointer is None:
        raise RuntimeError("Graph runtime is not started")
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
    if _compiled_graph is None:
        raise RuntimeError("Graph runtime is not started")
    return _compiled_graph
