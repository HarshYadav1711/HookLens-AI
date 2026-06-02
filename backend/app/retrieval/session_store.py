"""Persist ingest sessions and index fingerprints (metadata separate from vectors)."""

import hashlib
import json
import os
from typing import Any

from pydantic import BaseModel, Field

from app.config import get_settings
from app.models.video import NormalizedVideo


class SessionRecord(BaseModel):
    session_id: str
    fingerprint: str
    indexed_fingerprint: str | None = None
    video_a: NormalizedVideo = Field(description="YouTube (label A)")
    video_b: NormalizedVideo = Field(description="Instagram (label B)")


def transcript_fingerprint(video_a: NormalizedVideo, video_b: NormalizedVideo) -> str:
    parts: list[str] = []
    for label, video in [("A", video_a), ("B", video_b)]:
        for seg in video.transcript:
            parts.append(f"{label}|{seg.start_seconds}|{seg.end_seconds}|{seg.text}")
    digest = hashlib.sha256("\n".join(parts).encode()).hexdigest()
    return digest


def _session_path(session_id: str) -> str:
    settings = get_settings()
    base = os.path.join(settings.data_dir, "sessions")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, f"{session_id}.json")


def save_session(
    session_id: str,
    video_a: NormalizedVideo,
    video_b: NormalizedVideo,
) -> SessionRecord:
    record = SessionRecord(
        session_id=session_id,
        fingerprint=transcript_fingerprint(video_a, video_b),
        video_a=video_a,
        video_b=video_b,
    )
    path = _session_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record.model_dump(mode="json"), f, indent=2)
    return record


def load_session(session_id: str) -> SessionRecord | None:
    path = _session_path(session_id)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
    return SessionRecord.model_validate(data)


def mark_indexed(session_id: str, fingerprint: str) -> None:
    record = load_session(session_id)
    if not record:
        raise FileNotFoundError(f"Session not found: {session_id}")
    record.indexed_fingerprint = fingerprint
    path = _session_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record.model_dump(mode="json"), f, indent=2)
