import re
from urllib.parse import parse_qs, urlparse

from app.models.video import VideoPlatform
from app.utils.errors import UnsupportedUrlError

YOUTUBE_PATTERNS = [
    re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})"),
]

INSTAGRAM_PATTERNS = [
    re.compile(r"instagram\.com/reels/([A-Za-z0-9_-]+)"),
    re.compile(r"instagram\.com/reel/([A-Za-z0-9_-]+)"),
    re.compile(r"instagram\.com/p/([A-Za-z0-9_-]+)"),
]


def validate_youtube_url(url: str) -> str:
    if "youtube.com" not in url and "youtu.be" not in url:
        raise UnsupportedUrlError("youtube_url must be a valid YouTube link")
    return extract_youtube_id(url)


def validate_instagram_url(url: str) -> str:
    if "instagram.com" not in url:
        raise UnsupportedUrlError("instagram_url must be a valid Instagram Reel or post link")
    video_id = extract_instagram_id(url)
    if not video_id:
        raise UnsupportedUrlError("Could not parse Instagram content ID from URL")
    return video_id


def extract_youtube_id(url: str) -> str:
    for pattern in YOUTUBE_PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group(1)
    parsed = urlparse(url)
    if parsed.hostname and "youtube" in parsed.hostname:
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"][0]:
            return qs["v"][0]
    raise UnsupportedUrlError(f"Could not parse YouTube video ID from URL: {url}")


def extract_instagram_id(url: str) -> str | None:
    cleaned = url.strip()
    for pattern in INSTAGRAM_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            return match.group(1)
    return None


def platform_label(platform: VideoPlatform) -> str:
    return "YouTube" if platform == VideoPlatform.YOUTUBE else "Instagram"
