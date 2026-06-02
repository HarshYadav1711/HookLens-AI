def compute_engagement_rate(
    views: int | None,
    likes: int | None,
    comments: int | None,
) -> float | None:
    """Engagement rate = (likes + comments) / views × 100. Returns None when views missing or zero."""
    if views is None or views <= 0:
        return None
    return round((((likes or 0) + (comments or 0)) / views) * 100, 4)
