"""yt-dlp wrappers for metadata extraction and audio download."""

import os
from typing import Any

import yt_dlp

from app.utils.errors import MetadataExtractionError


def extract_metadata(url: str) -> dict[str, Any]:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        raise MetadataExtractionError(f"yt-dlp metadata failed: {exc}") from exc

    if not info:
        raise MetadataExtractionError("yt-dlp returned empty metadata")
    return dict(info)


def download_audio(url: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    out_template = os.path.join(out_dir, "%(id)s.%(ext)s")
    opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as exc:
        raise MetadataExtractionError(f"yt-dlp audio download failed: {exc}") from exc

    video_id = info.get("id", "audio")
    wav_path = os.path.join(out_dir, f"{video_id}.wav")
    if os.path.isfile(wav_path):
        return wav_path

    for name in os.listdir(out_dir):
        if name.startswith(str(video_id)) and name.endswith((".wav", ".m4a", ".webm", ".mp3")):
            return os.path.join(out_dir, name)

    raise MetadataExtractionError(f"Audio file not found after download for {url}")
