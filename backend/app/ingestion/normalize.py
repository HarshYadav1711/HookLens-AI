"""Map raw yt-dlp / platform payloads into NormalizedVideo fields."""

import re
from datetime import datetime
from typing import Any

from app.models.video import ExtractionStatus, NormalizedVideo, VideoPlatform
from app.services.engagement import compute_engagement_rate


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_upload_date(raw: Any) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        digits = re.sub(r"\D", "", raw)
        if len(digits) == 8:
            try:
                return datetime.strptime(digits, "%Y%m%d").date().isoformat()
            except ValueError:
                return None
        return raw if raw else None
    return None


def _extract_hashtags(raw: dict[str, Any]) -> list[str] | None:
    tags = raw.get("tags")
    if isinstance(tags, list) and tags:
        normalized = [str(t).lstrip("#") for t in tags if t]
        return normalized or None

    description = raw.get("description") or ""
    if isinstance(description, str) and "#" in description:
        found = re.findall(r"#(\w+)", description)
        return found or None

    return None


def _pick_views(raw: dict[str, Any]) -> int | None:
    for key in ("view_count", "play_count", "view_count_raw"):
        val = _safe_int(raw.get(key))
        if val is not None:
            return val
    return None


def _pick_creator(raw: dict[str, Any]) -> str | None:
    for key in ("uploader", "channel", "creator", "uploader_id"):
        val = raw.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _pick_follower_count(raw: dict[str, Any]) -> int | None:
    for key in ("channel_follower_count", "follower_count", "uploader_follower_count"):
        val = _safe_int(raw.get(key))
        if val is not None:
            return val
    return None


def build_normalized_from_metadata(
    *,
    platform: VideoPlatform,
    url: str,
    video_id: str,
    raw: dict[str, Any] | None,
    metadata_ok: bool,
) -> NormalizedVideo:
    if not raw:
        return NormalizedVideo(
            platform=platform,
            url=url,
            video_id=video_id,
            metadata_status=ExtractionStatus.FAILED,
            warnings=["Metadata extraction returned no data"],
        )

    views = _pick_views(raw)
    likes = _safe_int(raw.get("like_count"))
    comments = _safe_int(raw.get("comment_count"))
    title = raw.get("title")
    title_str = title.strip() if isinstance(title, str) and title.strip() else None

    video = NormalizedVideo(
        platform=platform,
        url=url,
        video_id=video_id,
        title=title_str,
        creator=_pick_creator(raw),
        upload_date=_normalize_upload_date(raw.get("upload_date") or raw.get("release_date")),
        duration_seconds=_safe_float(raw.get("duration")),
        views=views,
        likes=likes,
        comments=comments,
        hashtags=_extract_hashtags(raw),
        follower_count=_pick_follower_count(raw),
        engagement_rate=compute_engagement_rate(views, likes, comments),
        metadata_status=ExtractionStatus.COMPLETE if metadata_ok else ExtractionStatus.PARTIAL,
        raw_metadata={
            k: raw.get(k)
            for k in (
                "view_count",
                "play_count",
                "like_count",
                "comment_count",
                "duration",
                "upload_date",
                "uploader",
                "channel",
                "channel_follower_count",
            )
            if raw.get(k) is not None
        },
    )

    if not metadata_ok:
        video.warnings.append("Metadata extraction was partial or incomplete")
    if video.views is None:
        video.warnings.append("View count unavailable")
    if video.engagement_rate is None:
        video.warnings.append("Engagement rate unavailable (missing or zero views)")

    return video
