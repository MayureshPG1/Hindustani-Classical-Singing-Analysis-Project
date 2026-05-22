"""Load two recordings, extract pitch, and build ComparisonResult."""

from __future__ import annotations

from pathlib import Path

from backend.app.core import config
from backend.app.core.errors import raise_no_vocals_detected
from backend.app.core.request_log import log_event, log_step
from backend.app.models.comparison import ComparisonResult
from backend.app.models.pitch import PitchFrame, PitchSummary
from backend.app.services.audio_loader import LoadedAudio, load_and_validate
from backend.app.services.pitch_extractor import extract_pitch

ROUTE = "POST /compare"


def summarize_pitch(frames: list[PitchFrame]) -> PitchSummary:
    total = len(frames)
    voiced_count = sum(1 for frame in frames if frame.voiced)
    fraction = voiced_count / total if total else 0.0
    return PitchSummary(
        voiced_frame_count=voiced_count,
        total_frame_count=total,
        voiced_fraction=round(fraction, 4),
    )


def ensure_sufficient_vocals(frames: list[PitchFrame], *, role: str) -> None:
    """Raise no_vocals_detected when pitch is too sparse for the role."""
    summary = summarize_pitch(frames)
    if summary.voiced_frame_count < config.MIN_VOICED_FRAMES_TOTAL:
        raise_no_vocals_detected(role=role, summary=summary)
    if summary.voiced_fraction < config.MIN_VOICED_FRACTION:
        raise_no_vocals_detected(role=role, summary=summary)


def compare_audio_files(
    guru_path: Path,
    *,
    guru_file_name: str,
    guru_file_id: str | None = None,
    disciple_path: Path,
    disciple_file_name: str,
    disciple_file_id: str | None = None,
) -> ComparisonResult:
    """
    Load guru and disciple audio, extract full-timeline pitch for each.

    Preserves timelines; does not trim, align, or score.
    """
    with log_step(ROUTE, "load guru", path=str(guru_path)):
        guru_loaded: LoadedAudio = load_and_validate(
            guru_path,
            role="guru",
            file_name=guru_file_name,
            file_id=guru_file_id,
        )

    with log_step(ROUTE, "extract_pitch guru", duration_s=guru_loaded.file_info.duration_seconds):
        guru_frames = extract_pitch(
            guru_loaded.waveform,
            sample_rate=guru_loaded.sample_rate,
            route=ROUTE,
        )

    with log_step(ROUTE, "load disciple", path=str(disciple_path)):
        disciple_loaded: LoadedAudio = load_and_validate(
            disciple_path,
            role="disciple",
            file_name=disciple_file_name,
            file_id=disciple_file_id,
        )

    with log_step(
        ROUTE,
        "extract_pitch disciple",
        duration_s=disciple_loaded.file_info.duration_seconds,
    ):
        disciple_frames = extract_pitch(
            disciple_loaded.waveform,
            sample_rate=disciple_loaded.sample_rate,
            route=ROUTE,
        )

    with log_step(ROUTE, "vocal_check guru"):
        ensure_sufficient_vocals(guru_frames, role="guru")
    with log_step(ROUTE, "vocal_check disciple"):
        ensure_sufficient_vocals(disciple_frames, role="disciple")

    log_event(
        ROUTE,
        "comparison ready",
        guru_frames=len(guru_frames),
        disciple_frames=len(disciple_frames),
    )

    return ComparisonResult(
        guru_file_info=guru_loaded.file_info,
        disciple_file_info=disciple_loaded.file_info,
        guru_pitch_frames=guru_frames,
        disciple_pitch_frames=disciple_frames,
        guru_summary=summarize_pitch(guru_frames),
        disciple_summary=summarize_pitch(disciple_frames),
        warnings=[],
    )
