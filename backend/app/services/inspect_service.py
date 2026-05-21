"""Validate upload and return file info with pitch preview (first N frames)."""

from __future__ import annotations

from pathlib import Path

from backend.app.core import config
from backend.app.models.audio import AudioInspectResponse, PitchMetadata
from backend.app.services.audio_loader import load_and_validate
from backend.app.services.compare_service import ensure_sufficient_vocals, summarize_pitch
from backend.app.services.pitch_extractor import extract_pitch


def inspect_audio_file(
    path: Path,
    *,
    role: str,
    file_name: str,
    file_id: str | None = None,
) -> AudioInspectResponse:
    """
    Load audio, extract pitch for validation, return metadata and pitch preview.

    The API returns only the first ``INSPECT_PITCH_PREVIEW_FRAMES`` frames;
    the full timeline is produced on ``POST /compare``.
    """
    loaded = load_and_validate(path, role=role, file_name=file_name, file_id=file_id)
    frames = extract_pitch(loaded.waveform, sample_rate=loaded.sample_rate)
    ensure_sufficient_vocals(frames, role=role)
    summary = summarize_pitch(frames)
    preview_count = config.INSPECT_PITCH_PREVIEW_FRAMES

    return AudioInspectResponse(
        file_info=loaded.file_info,
        pitch_metadata=PitchMetadata(
            voiced_frame_count=summary.voiced_frame_count,
            total_frame_count=summary.total_frame_count,
            voiced_fraction=summary.voiced_fraction,
            preview_frames=frames[:preview_count],
        ),
    )
