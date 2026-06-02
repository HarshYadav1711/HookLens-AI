from app.graph.citations import assemble_citations, build_prompts
from app.graph.reasoning import build_comparison_facts
from app.ingestion.normalize import build_normalized_from_metadata
from app.models.video import TranscriptSegment, VideoPlatform
from app.retrieval.retriever import RetrievalHit
from app.retrieval.session_store import SessionRecord


def _video(platform: VideoPlatform, vid: str, views: int | None, rate: float | None):
    base = build_normalized_from_metadata(
        platform=platform,
        url=f"https://example.com/{vid}",
        video_id=vid,
        raw={
            "title": f"{vid} title",
            "uploader": "Creator",
            "view_count": views,
            "like_count": 10,
            "comment_count": 5,
        },
        metadata_ok=True,
    )
    return base.model_copy(
        update={
            "engagement_rate": rate,
            "transcript": [TranscriptSegment(start_seconds=0, end_seconds=1, text="hook line")],
        }
    )


def test_comparison_facts_are_deterministic_and_label_videos():
    record = SessionRecord(
        session_id="s1",
        fingerprint="fp",
        video_a=_video(VideoPlatform.YOUTUBE, "yt", 1000, 1.5),
        video_b=_video(VideoPlatform.INSTAGRAM, "ig", 500, 3.0),
    )
    facts = build_comparison_facts(record)
    assert "Video A (YouTube)" in facts
    assert "Video B (Instagram)" in facts
    assert "Higher engagement rate: B (Instagram)" in facts
    assert "1.5%" in facts
    assert "3.0%" in facts


def test_citation_assembly_numbers_chunks_and_preserves_traceability():
    hits = [
        RetrievalHit(
            session_id="s1",
            video_label="A",
            video_id="yt",
            chunk_id="c1",
            chunk_index=0,
            start_time=0.0,
            end_time=2.5,
            text="Retention hook in first three seconds.",
            platform="youtube",
            url="https://youtube.com/watch?v=yt",
            title="YT",
            score=0.9,
        ),
        RetrievalHit(
            session_id="s1",
            video_label="B",
            video_id="ig",
            chunk_id="c2",
            chunk_index=1,
            start_time=1.0,
            end_time=4.0,
            text="Reel trend angle here.",
            platform="instagram",
            url="https://instagram.com/reel/ig",
            title="IG",
            score=0.8,
        ),
    ]
    citations, evidence = assemble_citations(hits)
    assert len(citations) == 2
    assert citations[0]["index"] == 1
    assert citations[1]["video_label"] == "B"
    assert "[1]" in evidence and "chunk_id=c1" in evidence
    assert "[2]" in evidence

    system, user = build_prompts("FACTS", evidence, "Why did B win?")
    assert "Never invent" in system
    assert "FACTS" in user
    assert "[1]" in user
