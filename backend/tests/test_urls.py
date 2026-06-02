import pytest

from app.utils.errors import UnsupportedUrlError
from app.utils.urls import extract_youtube_id, validate_instagram_url, validate_youtube_url


def test_extract_youtube_id():
    assert extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_invalid_youtube_raises():
    with pytest.raises(UnsupportedUrlError):
        validate_youtube_url("https://example.com/video")


def test_validate_instagram_reel():
    assert validate_instagram_url("https://www.instagram.com/reel/ABC123xyz/") == "ABC123xyz"
