from app.ingestion.normalize import build_normalized_from_metadata
from app.models.video import ExtractionStatus, VideoPlatform


def test_engagement_rate_from_raw_metadata():
    video = build_normalized_from_metadata(
        platform=VideoPlatform.YOUTUBE,
        url="https://youtube.com/watch?v=abc",
        video_id="abc",
        raw={
            "title": "Test Video",
            "uploader": "Creator",
            "view_count": 1000,
            "like_count": 50,
            "comment_count": 10,
            "duration": 120,
            "upload_date": "20240115",
        },
        metadata_ok=True,
    )
    assert video.title == "Test Video"
    assert video.creator == "Creator"
    assert video.upload_date == "2024-01-15"
    assert video.engagement_rate == 6.0
    assert video.metadata_status == ExtractionStatus.COMPLETE


def test_missing_views_yields_null_engagement():
    video = build_normalized_from_metadata(
        platform=VideoPlatform.INSTAGRAM,
        url="https://instagram.com/reel/x",
        video_id="x",
        raw={"title": "Reel", "like_count": 5},
        metadata_ok=True,
    )
    assert video.views is None
    assert video.engagement_rate is None
    assert any("Engagement rate unavailable" in w for w in video.warnings)
