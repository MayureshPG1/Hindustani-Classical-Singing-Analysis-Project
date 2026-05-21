"""Sa detection from pitch frames (Phase 4)."""

from __future__ import annotations

from dataclasses import dataclass

import librosa
import numpy as np

from backend.app.core import config
from backend.app.core.errors import (
    raise_no_vocals_detected,
    raise_sa_detection_failed,
)
from backend.app.models.comparison import PitchFrame

SA_HISTOGRAM_BINS = 12
STABILITY_WINDOW_FRAMES = 5


@dataclass(frozen=True)
class SaDetectionResult:
    """Detected tonic for one recording."""

    sa_hz: float
    confidence: float


def _frames_for_sa_estimation(frames: list[PitchFrame]) -> list[PitchFrame]:
    """High-confidence voiced frames used only for Sa histogram (timeline unchanged)."""
    eligible: list[PitchFrame] = []
    for frame in frames:
        if frame.frequency_hz is None:
            continue
        confidence = frame.confidence if frame.confidence is not None else 0.0
        if confidence >= config.VOICED_PROB_SA_MIN:
            eligible.append(frame)
    return eligible


def _pitch_class_bin(frequency_hz: float) -> int:
    midi = librosa.hz_to_midi(frequency_hz)
    pitch_class_cents = (float(midi) % 12.0) * 100.0
    return int(round(pitch_class_cents / 100.0)) % SA_HISTOGRAM_BINS


def _stability_weights(log_frequencies: np.ndarray) -> np.ndarray:
    n = len(log_frequencies)
    weights = np.ones(n, dtype=np.float64)
    half = STABILITY_WINDOW_FRAMES
    for index in range(n):
        start = max(0, index - half)
        end = min(n, index + half + 1)
        local_std = float(np.std(log_frequencies[start:end]))
        weights[index] = 1.0 / (1.0 + local_std * 200.0)
    return weights


def ensure_vocals_present(frames: list[PitchFrame]) -> None:
    """Raise no_vocals_detected when plot-level voiced content is too sparse."""
    if not frames:
        raise_no_vocals_detected(voiced_frame_count=0, total_frame_count=0)

    voiced_count = sum(1 for frame in frames if frame.voiced)
    if voiced_count < config.MIN_VOICED_FRAMES_TOTAL:
        raise_no_vocals_detected(
            voiced_frame_count=voiced_count,
            total_frame_count=len(frames),
        )

    voiced_fraction = voiced_count / len(frames)
    if voiced_fraction < config.MIN_VOICED_FRACTION:
        raise_no_vocals_detected(
            voiced_frame_count=voiced_count,
            total_frame_count=len(frames),
        )


def detect_sa(frames: list[PitchFrame]) -> SaDetectionResult:
    """
    Estimate Sa (tonic) Hz from reliable pitch frames.

    Uses a weighted pitch-class histogram (confidence × local stability).
    """
    ensure_vocals_present(frames)

    sa_frames = _frames_for_sa_estimation(frames)
    if len(sa_frames) < config.SA_MIN_VOICED_FRAMES:
        raise_sa_detection_failed(sa_frame_count=len(sa_frames))

    frequencies = np.array([frame.frequency_hz for frame in sa_frames], dtype=np.float64)
    confidences = np.array(
        [frame.confidence if frame.confidence is not None else 0.0 for frame in sa_frames],
        dtype=np.float64,
    )
    log_frequencies = np.log2(frequencies)
    stability = _stability_weights(log_frequencies)
    sample_weights = confidences * stability

    histogram = np.zeros(SA_HISTOGRAM_BINS, dtype=np.float64)
    bin_indices = np.array([_pitch_class_bin(float(f)) for f in frequencies], dtype=int)
    for bin_index, weight in zip(bin_indices, sample_weights, strict=True):
        histogram[bin_index] += weight

    total_weight = float(histogram.sum())
    if total_weight <= 0.0:
        raise_sa_detection_failed(sa_frame_count=len(sa_frames))

    peak_bin = int(np.argmax(histogram))
    peak_weight = float(histogram[peak_bin])
    peak_fraction = peak_weight / total_weight

    if peak_fraction < config.SA_HISTOGRAM_MIN_PEAK_WEIGHT:
        raise_sa_detection_failed(
            sa_frame_count=len(sa_frames),
            peak_weight_fraction=peak_fraction,
        )

    peak_mask = bin_indices == peak_bin
    sa_hz = float(np.median(frequencies[peak_mask]))

    return SaDetectionResult(sa_hz=sa_hz, confidence=peak_fraction)


def hz_to_cents_from_sa(frequency_hz: float, sa_hz: float) -> float:
    """Cents relative to detected Sa (may exceed one octave)."""
    return float(1200.0 * np.log2(frequency_hz / sa_hz))
