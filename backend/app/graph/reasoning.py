"""Deterministic comparison context from session metadata (no LLM)."""

from app.models.video import NormalizedVideo
from app.retrieval.session_store import SessionRecord


def _fmt_metric(label: str, value: str | None) -> str:
    return f"{label}: {value if value is not None else 'unavailable'}"


def _video_facts(label: str, video: NormalizedVideo) -> list[str]:
    platform_name = "YouTube" if video.platform.value == "youtube" else "Instagram"
    lines = [
        f"Video {label} ({platform_name})",
        _fmt_metric("  title", video.title),
        _fmt_metric("  creator", video.creator),
        _fmt_metric("  upload_date", video.upload_date),
        _fmt_metric("  duration_seconds", str(video.duration_seconds) if video.duration_seconds is not None else None),
        _fmt_metric("  views", str(video.views) if video.views is not None else None),
        _fmt_metric("  likes", str(video.likes) if video.likes is not None else None),
        _fmt_metric("  comments", str(video.comments) if video.comments is not None else None),
        _fmt_metric("  engagement_rate_pct", f"{video.engagement_rate}%" if video.engagement_rate is not None else None),
        _fmt_metric("  transcript_status", video.transcript_status.value),
    ]
    if video.hashtags:
        lines.append(f"  hashtags: {', '.join(video.hashtags)}")
    if video.follower_count is not None:
        lines.append(f"  follower_count: {video.follower_count}")
    return lines


def build_comparison_facts(record: SessionRecord) -> str:
    """Structured, factual comparison context derived only from ingested metadata."""
    a = record.video_a
    b = record.video_b
    lines = ["=== Comparison facts (from platform metadata; do not invent values) ==="]
    lines.extend(_video_facts("A", a))
    lines.append("")
    lines.extend(_video_facts("B", b))
    lines.append("")

    if a.engagement_rate is not None and b.engagement_rate is not None:
        if a.engagement_rate > b.engagement_rate:
            winner = "A (YouTube)"
        elif b.engagement_rate > a.engagement_rate:
            winner = "B (Instagram)"
        else:
            winner = "tie"
        lines.append(
            f"Higher engagement rate: {winner} "
            f"(A={a.engagement_rate}%, B={b.engagement_rate}%)"
        )
    else:
        lines.append("Higher engagement rate: unavailable (insufficient view counts)")

    return "\n".join(lines)
