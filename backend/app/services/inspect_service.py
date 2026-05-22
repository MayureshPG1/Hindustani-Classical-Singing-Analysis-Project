"""Validate upload and return file info with full-timeline pitch stats."""

from __future__ import annotations

from pathlib import Path

from backend.app.core.request_log import log_event, log_step
from backend.app.models.audio import AudioInspectResponse, PitchMetadata
from backend.app.models.pitch import PitchFrame
from backend.app.services.audio_loader import load_and_validate
from backend.app.services.compare_service import ensure_sufficient_vocals, summarize_pitch
from backend.app.services.pitch_extractor import extract_pitch

ROUTE = "POST /audio/inspect"


def inspect_audio_file(
    path: Path,
    *,
    role: str,
    file_name: str,
    file_id: str | None = None,
) -> tuple[AudioInspectResponse, list[PitchFrame]]:
    """
    Load audio, extract pitch for validation, return metadata and voiced stats.

    Pitch frames are stored in the session at inspect and reused at compare.
    """
    with log_step(ROUTE, "load_and_validate", path=str(path), role=role):
        loaded = load_and_validate(path, role=role, file_name=file_name, file_id=file_id)

    with log_step(ROUTE, "extract_pitch", duration_s=loaded.file_info.duration_seconds):
        frames = extract_pitch(
            loaded.waveform,
            sample_rate=loaded.sample_rate,
            route=ROUTE,
        )

    with log_step(ROUTE, "vocal_check", role=role):
        ensure_sufficient_vocals(frames, role=role)

    summary = summarize_pitch(frames)

    log_event(
        ROUTE,
        "pitch summary",
        voiced_frame_count=summary.voiced_frame_count,
        total_frame_count=summary.total_frame_count,
        voiced_fraction=summary.voiced_fraction,
    )

    response = AudioInspectResponse(
        file_info=loaded.file_info,
        pitch_metadata=PitchMetadata(
            voiced_frame_count=summary.voiced_frame_count,
            total_frame_count=summary.total_frame_count,
            voiced_fraction=summary.voiced_fraction,
        ),
    )
    return response, frames
