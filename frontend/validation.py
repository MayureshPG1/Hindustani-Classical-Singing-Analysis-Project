"""Client-side upload validation before API inspect."""

from __future__ import annotations

import wave
from pathlib import Path

from shared.constants import MAX_AUDIO_DURATION_SECONDS, SUPPORTED_AUDIO_EXTENSIONS

FILE_TOO_LONG_MESSAGE = "Audio file must be 5 minutes or shorter."


def validate_upload_path(path: Path) -> str | None:
    """Return an error message if the file fails client checks, else None."""
    if not path.exists():
        return "File does not exist."
    if path.stat().st_size <= 0:
        return "File is empty."
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_AUDIO_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))
        return f"Unsupported file type. Use: {supported}."
    duration = read_duration_seconds(path)
    if duration is not None and duration > MAX_AUDIO_DURATION_SECONDS:
        return FILE_TOO_LONG_MESSAGE
    return None


def read_duration_seconds(path: Path) -> float | None:
    """Best-effort local duration in seconds; None if metadata is unavailable."""
    suffix = path.suffix.lower()
    if suffix == ".wav":
        return _wav_duration_seconds(path)
    return None


def _wav_duration_seconds(path: Path) -> float | None:
    try:
        import soundfile as sf

        info = sf.info(path)
        if info.duration and info.duration > 0:
            return float(info.duration)
    except Exception:
        pass

    try:
        with wave.open(str(path), "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            if rate > 0:
                return frames / float(rate)
    except Exception:
        return None
    return None
