"""Local Ollama chat completions (streaming and non-streaming)."""

import json
from collections.abc import AsyncIterator

import httpx

from app.config import get_settings


async def stream_chat(
    system_prompt: str,
    user_prompt: str,
    history: list[dict[str, str]] | None = None,
) -> AsyncIterator[str]:
    settings = get_settings()
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    payload = {"model": settings.ollama_model, "messages": messages, "stream": True}

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get("done"):
                    break
                msg = data.get("message") or {}
                token = msg.get("content")
                if token:
                    yield token


async def check_ollama() -> bool:
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
            return response.status_code == 200
    except Exception:
        return False
