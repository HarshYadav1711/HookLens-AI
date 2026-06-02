"""Local speech-to-text fallback using faster-whisper."""

import os

from app.config import get_settings
from app.models.video import TranscriptSegment, TranscriptSource, TranscriptStatus
from app.utils.errors import TranscriptExtractionError

_whisper_model = None


def _get_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel

        settings = get_settings()
        _whisper_model = WhisperModel(
            settings.whisper_model_size,
            device="cpu",
            compute_type="int8",
        )
    return _whisper_model


def transcribe_audio_file(audio_path: str) -> tuple[list[TranscriptSegment], TranscriptSource, TranscriptStatus]:
    if not os.path.isfile(audio_path):
        raise TranscriptExtractionError(f"Audio file not found: {audio_path}")

    try:
        model = _get_model()
        segments_iter, _info = model.transcribe(audio_path, beam_size=5, vad_filter=True)
        segments: list[TranscriptSegment] = []
        for seg in segments_iter:
            text = (seg.text or "").strip()
            if text:
                segments.append(
                    TranscriptSegment(
                        start_seconds=float(seg.start),
                        end_seconds=float(seg.end),
                        text=text,
                    )
                )
    except Exception as exc:
        raise TranscriptExtractionError(f"Whisper transcription failed: {exc}") from exc
    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass

    if not segments:
        return [], TranscriptSource.UNAVAILABLE, TranscriptStatus.UNAVAILABLE
    return segments, TranscriptSource.FASTER_WHISPER, TranscriptStatus.AVAILABLE
