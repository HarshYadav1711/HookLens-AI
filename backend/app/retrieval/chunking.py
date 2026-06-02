"""Segment-aware transcript chunking that preserves utterance and sentence boundaries."""

import hashlib
import re

from app.models.chunk import ChunkSourceMeta, TranscriptChunk, VideoLabel
from app.models.video import NormalizedVideo, TranscriptSegment, VideoPlatform

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
WORD_SPLIT = re.compile(r"\s+")

# YouTube = A, Instagram = B
PLATFORM_LABEL: dict[VideoPlatform, VideoLabel] = {
    VideoPlatform.YOUTUBE: "A",
    VideoPlatform.INSTAGRAM: "B",
}


def _chunk_id(session_id: str, video_label: VideoLabel, chunk_index: int) -> str:
    raw = f"{session_id}:{video_label}:{chunk_index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _split_long_text(text: str, max_chars: int) -> list[str]:
    """Split oversized text on sentence boundaries, then words as last resort."""
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []

    parts: list[str] = []
    sentences = SENTENCE_SPLIT.split(text)
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            parts.append(" ".join(buffer).strip())

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        candidate = " ".join(buffer + [sentence])
        if len(candidate) <= max_chars:
            buffer.append(sentence)
        else:
            flush()
            buffer = []
            if len(sentence) <= max_chars:
                buffer = [sentence]
            else:
                words = WORD_SPLIT.split(sentence)
                word_buf: list[str] = []
                for word in words:
                    cand = " ".join(word_buf + [word])
                    if len(cand) <= max_chars:
                        word_buf.append(word)
                    else:
                        if word_buf:
                            parts.append(" ".join(word_buf))
                        word_buf = [word] if len(word) <= max_chars else []
                        if len(word) > max_chars:
                            for i in range(0, len(word), max_chars):
                                parts.append(word[i : i + max_chars])
                if word_buf:
                    parts.append(" ".join(word_buf))
    flush()
    return [p for p in parts if p]


def _overlap_tail(text: str, max_chars: int) -> str:
    """Take trailing sentences up to max_chars for chunk overlap."""
    if not text or max_chars <= 0:
        return ""
    sentences = SENTENCE_SPLIT.split(text.strip())
    tail: list[str] = []
    total = 0
    for sentence in reversed(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
        add_len = len(sentence) + (1 if tail else 0)
        if total + add_len > max_chars:
            break
        tail.insert(0, sentence)
        total += add_len
    return " ".join(tail)


def chunk_video_transcript(
    video: NormalizedVideo,
    *,
    session_id: str,
    video_label: VideoLabel,
    max_chars: int,
    overlap_chars: int,
) -> list[TranscriptChunk]:
    segments = video.transcript
    if not segments:
        return []

    source = ChunkSourceMeta(
        platform=video.platform,
        url=video.url,
        title=video.title,
        creator=video.creator,
        transcript_source=video.transcript_source.value,
    )

    chunks: list[TranscriptChunk] = []
    chunk_index = 0
    seg_buffer: list[TranscriptSegment] = []
    overlap_prefix = ""

    def flush_buffer() -> None:
        nonlocal chunk_index, seg_buffer, overlap_prefix
        if not seg_buffer:
            return

        body = " ".join(s.text.strip() for s in seg_buffer if s.text.strip())
        if overlap_prefix:
            body = f"{overlap_prefix} {body}".strip()

        start_time = seg_buffer[0].start_seconds
        end_time = seg_buffer[-1].end_seconds

        for part in _split_long_text(body, max_chars):
            chunks.append(
                TranscriptChunk(
                    chunk_id=_chunk_id(session_id, video_label, chunk_index),
                    session_id=session_id,
                    video_label=video_label,
                    video_id=video.video_id,
                    chunk_index=chunk_index,
                    start_time=start_time,
                    end_time=end_time,
                    text=part,
                    source=source,
                )
            )
            chunk_index += 1

        overlap_prefix = _overlap_tail(body, overlap_chars)
        seg_buffer = []

    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue

        candidate_segments = seg_buffer + [segment]
        candidate_text = " ".join(
            s.text.strip() for s in candidate_segments if s.text.strip()
        )
        if overlap_prefix:
            candidate_text = f"{overlap_prefix} {candidate_text}"

        if seg_buffer and len(candidate_text) > max_chars:
            flush_buffer()
            seg_buffer = [segment]
        else:
            seg_buffer.append(segment)

    flush_buffer()
    return chunks


def chunk_session_pair(
    session_id: str,
    youtube: NormalizedVideo,
    instagram: NormalizedVideo,
    *,
    max_chars: int,
    overlap_chars: int,
) -> list[TranscriptChunk]:
    youtube_chunks = chunk_video_transcript(
        youtube,
        session_id=session_id,
        video_label="A",
        max_chars=max_chars,
        overlap_chars=overlap_chars,
    )
    instagram_chunks = chunk_video_transcript(
        instagram,
        session_id=session_id,
        video_label="B",
        max_chars=max_chars,
        overlap_chars=overlap_chars,
    )
    return youtube_chunks + instagram_chunks
