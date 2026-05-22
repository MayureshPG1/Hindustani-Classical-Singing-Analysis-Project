"""F0 extraction via librosa.pyin (Phase 3)."""

from __future__ import annotations

import numpy as np
import librosa

from backend.app.core import config
from backend.app.core.request_log import log_event, log_step, should_log
from backend.app.models.pitch import PitchFrame


def _classify_frame(
    frequency_hz: float | None,
    voiced_probability: float,
    pyin_voiced: bool,
) -> tuple[bool, bool, float | None]:
    """
    Map pyin output to voiced / silent_or_unvoiced flags.

    Uses architecture thresholds:
    - prob <= VOICED_PROB_SILENT_MAX -> silent/unvoiced
    - prob >= VOICED_PROB_PLOT_MIN and valid F0 -> voiced (reliable pitch)
    """
    has_f0 = frequency_hz is not None and frequency_hz > 0.0

    if voiced_probability <= config.VOICED_PROB_SILENT_MAX or not pyin_voiced or not has_f0:
        return False, True, None

    if voiced_probability >= config.VOICED_PROB_PLOT_MIN and has_f0:
        return True, False, frequency_hz

    return False, False, None


def extract_pitch(
    waveform: np.ndarray,
    *,
    sample_rate: int | None = None,
    route: str = "pitch",
) -> list[PitchFrame]:
    """
    Extract F0 with librosa.pyin over the full waveform timeline.

    Preserves every analysis frame (including silence); does not trim.
    """
    sr = sample_rate or config.SR
    if waveform.size == 0:
        log_event(route, "extract_pitch skipped empty waveform")
        return []

    hop = config.HOP_LENGTH
    if should_log():
        log_event(
            route,
            "pyin config",
            samples=len(waveform),
            sr=sr,
            hop_length=hop,
            frame_length=config.FRAME_LENGTH,
            n_thresholds=config.PYIN_N_THRESHOLDS,
            approx_frame_ms=round(1000 * hop / sr, 2),
        )

    with log_step(
        route,
        "librosa.pyin",
        samples=len(waveform),
        hop_length=hop,
    ):
        f0, voiced_flag, voiced_probs = librosa.pyin(
            waveform,
            fmin=config.FMIN_HZ,
            fmax=config.FMAX_HZ,
            sr=sr,
            frame_length=config.FRAME_LENGTH,
            hop_length=hop,
            n_thresholds=config.PYIN_N_THRESHOLDS,
        )

    times = librosa.frames_to_time(
        np.arange(len(f0)),
        sr=sr,
        hop_length=hop,
    )

    frames: list[PitchFrame] = []
    for time_s, raw_f0, pyin_voiced, prob in zip(times, f0, voiced_flag, voiced_probs):
        voiced_probability = float(prob) if prob is not None and not np.isnan(prob) else 0.0
        pyin_voiced_bool = bool(pyin_voiced)

        raw_hz: float | None = None
        if raw_f0 is not None and not np.isnan(raw_f0) and float(raw_f0) > 0.0:
            raw_hz = float(raw_f0)

        voiced, silent_or_unvoiced, frequency_hz = _classify_frame(
            raw_hz,
            voiced_probability,
            pyin_voiced_bool,
        )

        frames.append(
            PitchFrame(
                time_seconds=float(time_s),
                frequency_hz=frequency_hz,
                confidence=voiced_probability,
                voiced=voiced,
                silent_or_unvoiced=silent_or_unvoiced,
            )
        )

    if should_log():
        voiced_n = sum(1 for frame in frames if frame.voiced)
        log_event(
            route,
            "extract_pitch complete",
            frame_count=len(frames),
            voiced_frames=voiced_n,
        )

    return frames
