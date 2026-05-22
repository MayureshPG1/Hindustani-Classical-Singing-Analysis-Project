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


def _frames_from_pyin(
    f0: np.ndarray,
    voiced_flag: np.ndarray,
    voiced_probs: np.ndarray,
    *,
    sr: int,
    hop: int,
    time_offset_seconds: float,
) -> list[PitchFrame]:
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
                time_seconds=float(time_s) + time_offset_seconds,
                frequency_hz=frequency_hz,
                confidence=voiced_probability,
                voiced=voiced,
                silent_or_unvoiced=silent_or_unvoiced,
            )
        )
    return frames


def _run_pyin(waveform: np.ndarray, *, sr: int, hop: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return librosa.pyin(
        waveform,
        fmin=config.FMIN_HZ,
        fmax=config.FMAX_HZ,
        sr=sr,
        frame_length=config.FRAME_LENGTH,
        hop_length=hop,
    )


def extract_pitch(
    waveform: np.ndarray,
    *,
    sample_rate: int | None = None,
    route: str = "pitch",
) -> list[PitchFrame]:
    """
    Extract F0 with librosa.pyin over the full waveform timeline.

    Preserves every analysis frame (including silence); does not trim.
    With verbose logging, long audio is processed in chunks and each chunk logs
    an approximate percent complete.
    """
    sr = sample_rate or config.SR
    if waveform.size == 0:
        log_event(route, "extract_pitch skipped empty waveform")
        return []

    hop = config.HOP_LENGTH
    total_samples = len(waveform)
    chunk_samples = max(int(config.PYIN_CHUNK_SECONDS * sr), hop * 4)
    verbose = should_log()
    use_chunks = verbose and total_samples > chunk_samples

    if verbose:
        log_event(
            route,
            "pyin config",
            samples=total_samples,
            duration_s=round(total_samples / sr, 2),
            sr=sr,
            hop_length=hop,
            frame_length=config.FRAME_LENGTH,
            chunked=use_chunks,
            chunk_seconds=config.PYIN_CHUNK_SECONDS if use_chunks else None,
        )

    all_frames: list[PitchFrame] = []

    if not use_chunks:
        with log_step(route, "librosa.pyin", samples=total_samples):
            f0, voiced_flag, voiced_probs = _run_pyin(waveform, sr=sr, hop=hop)
        if verbose:
            log_event(route, "pyin progress", percent=100.0, chunk="1/1")
        all_frames = _frames_from_pyin(
            f0, voiced_flag, voiced_probs, sr=sr, hop=hop, time_offset_seconds=0.0
        )
    else:
        starts = list(range(0, total_samples, chunk_samples))
        num_chunks = len(starts)
        with log_step(route, "librosa.pyin chunked", chunks=num_chunks):
            for index, start in enumerate(starts):
                end = min(start + chunk_samples, total_samples)
                chunk = waveform[start:end]
                percent = round(100.0 * end / total_samples, 1)
                log_event(
                    route,
                    "pyin progress",
                    percent=percent,
                    chunk=f"{index + 1}/{num_chunks}",
                )
                f0, voiced_flag, voiced_probs = _run_pyin(chunk, sr=sr, hop=hop)
                all_frames.extend(
                    _frames_from_pyin(
                        f0,
                        voiced_flag,
                        voiced_probs,
                        sr=sr,
                        hop=hop,
                        time_offset_seconds=start / sr,
                    )
                )

    if verbose:
        voiced_n = sum(1 for frame in all_frames if frame.voiced)
        log_event(
            route,
            "extract_pitch complete",
            frame_count=len(all_frames),
            voiced_frames=voiced_n,
        )

    return all_frames
