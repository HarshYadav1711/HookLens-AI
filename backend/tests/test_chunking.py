from app.models.video import TranscriptSegment, TranscriptStatus, VideoPlatform
from app.ingestion.normalize import build_normalized_from_metadata
from app.retrieval.chunking import chunk_video_transcript


def _video_with_segments(segments: list[TranscriptSegment]):
    return build_normalized_from_metadata(
        platform=VideoPlatform.YOUTUBE,
        url="https://youtube.com/watch?v=test",
        video_id="test",
        raw={"title": "Demo"},
        metadata_ok=True,
    ).model_copy(update={"transcript": segments, "transcript_status": TranscriptStatus.AVAILABLE})


def test_chunks_respect_segment_boundaries():
    segments = [
        TranscriptSegment(start_seconds=0, end_seconds=2, text="First full sentence here."),
        TranscriptSegment(start_seconds=2, end_seconds=4, text="Second sentence stays intact."),
        TranscriptSegment(start_seconds=4, end_seconds=6, text="Third sentence for grouping."),
    ]
    video = _video_with_segments(segments)
    chunks = chunk_video_transcript(
        video, session_id="sess-1", video_label="A", max_chars=120, overlap_chars=20
    )
    assert chunks
    combined = " ".join(c.text for c in chunks)
    assert "First full sentence here." in combined
    assert "Second sentence stays intact." in combined
    assert "Third sentence for grouping." in combined
    for chunk in chunks:
        assert chunk.video_label == "A"
        assert chunk.video_id == "test"
        assert chunk.chunk_id
        assert chunk.start_time <= chunk.end_time
        assert chunk.source.platform == VideoPlatform.YOUTUBE


def test_long_segment_splits_on_sentences_not_arbitrary_mid_word():
    long = "Alpha beta gamma. " * 30
    segments = [TranscriptSegment(start_seconds=0, end_seconds=60, text=long.strip())]
    video = _video_with_segments(segments)
    chunks = chunk_video_transcript(
        video, session_id="sess-2", video_label="A", max_chars=80, overlap_chars=10
    )
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.text) <= 80 or chunk.text.endswith(".")


def test_empty_transcript_produces_no_chunks():
    video = _video_with_segments([])
    chunks = chunk_video_transcript(
        video, session_id="sess-3", video_label="B", max_chars=100, overlap_chars=10
    )
    assert chunks == []
