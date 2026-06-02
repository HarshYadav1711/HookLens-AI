from app.models.video import (
    TranscriptSegment,
    TranscriptSource,
    TranscriptStatus,
    VideoPlatform,
)
from app.ingestion.normalize import build_normalized_from_metadata
from app.retrieval.indexer import index_session
from app.retrieval.qdrant_store import _chunk_payload
from app.retrieval.chunking import chunk_session_pair
from app.retrieval.retriever import retrieve
from app.retrieval.session_store import save_session


def _sample_video(platform: VideoPlatform, video_id: str, lines: list[str]):
    segments = [
        TranscriptSegment(start_seconds=i * 2, end_seconds=(i + 1) * 2, text=t)
        for i, t in enumerate(lines)
    ]
    base = build_normalized_from_metadata(
        platform=platform,
        url=f"https://example.com/{video_id}",
        video_id=video_id,
        raw={"title": f"Title {video_id}", "uploader": "Creator", "view_count": 100},
        metadata_ok=True,
    )
    return base.model_copy(
        update={
            "transcript": segments,
            "transcript_status": TranscriptStatus.AVAILABLE,
            "transcript_source": TranscriptSource.YOUTUBE_TRANSCRIPT_API,
        }
    )


def test_chunk_payload_carries_citation_metadata_not_full_video_record(retrieval_env):
    youtube = _sample_video(VideoPlatform.YOUTUBE, "yt1", ["YouTube hook about retention."])
    instagram = _sample_video(VideoPlatform.INSTAGRAM, "ig1", ["Instagram reel about trends."])
    chunks = chunk_session_pair("sess-payload", youtube, instagram, max_chars=200, overlap_chars=20)
    payload = _chunk_payload(chunks[0])
    assert payload["video_label"] in ("A", "B")
    assert payload["chunk_id"]
    assert "start_time" in payload
    assert "end_time" in payload
    assert "text" in payload
    assert "engagement_rate" not in payload
    assert "raw_metadata" not in payload


def test_index_and_retrieve_with_video_label_filter(retrieval_env):
    session_id = "sess-retrieve"
    youtube = _sample_video(
        VideoPlatform.YOUTUBE,
        "yt1",
        ["YouTube exclusive keyword about watch time."],
    )
    instagram = _sample_video(
        VideoPlatform.INSTAGRAM,
        "ig1",
        ["Instagram exclusive keyword about reels."],
    )
    save_session(session_id, youtube, instagram)
    index_session(session_id, youtube, instagram)

    all_hits = retrieve(
        session_id, "YouTube exclusive keyword about watch time", top_k=5
    ).hits
    assert all_hits
    assert any(h.video_label == "A" for h in all_hits)

    only_a = retrieve(
        session_id,
        "YouTube exclusive keyword about watch time",
        video_label="A",
        top_k=5,
    ).hits
    assert only_a
    assert all(h.video_label == "A" for h in only_a)
    assert all(h.video_id == "yt1" for h in only_a)


def test_repeated_index_skips_reembedding(retrieval_env):
    session_id = "sess-reindex"
    youtube = _sample_video(VideoPlatform.YOUTUBE, "yt1", ["Stable transcript line."])
    instagram = _sample_video(VideoPlatform.INSTAGRAM, "ig1", ["Another stable line."])
    save_session(session_id, youtube, instagram)

    first = index_session(session_id, youtube, instagram)
    assert first.chunks_indexed > 0
    assert first.skipped_reindex is False

    second = index_session(session_id, youtube, instagram)
    assert second.skipped_reindex is True
    assert second.chunks_indexed == 0
    assert second.fingerprint == first.fingerprint
