"""Client-side upload validation before API inspect (Phase 7)."""

from __future__ import annotations

from pathlib import Path

from shared.constants import SUPPORTED_AUDIO_EXTENSIONS


def validate_upload_path(path: Path) -> str | None:
    """Return an error message if the file fails client checks, else None."""
    if not path.exists():
        return "File does not exist."
    if path.stat().st_size <= 0:
        return "File is empty."
    if path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
        return f"Unsupported file type. Use: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}."
    return None
