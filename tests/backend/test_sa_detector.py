"""Unit tests for sa_detector."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from backend.app.core import config
from backend.app.core.errors import HcsaError
from backend.app.models.comparison import PitchFrame
from backend.app.services.audio_loader import load_and_validate
from backend.app.services.pitch_extractor import extract_pitch
from backend.app.services.sa_detector import (
    SaDetectionResult,
    detect_sa,
    ensure_vocals_present,
    hz_to_cents_from_sa,
)
from tests.fixtures.audio_factory import write_wav


def _extract_frames(tmp_path: Path, frequency_hz: float, duration: float = 2.0) -> list[PitchFrame]:
    path = write_wav(
        tmp_path / f"tone_{frequency_hz}.wav",
        duration_seconds=duration,
        sample_rate=config.SR,
        frequency_hz=frequency_hz,
        amplitude=0.6,
    )
    loaded = load_and_validate(path, role="guru", file_name=path.name)
    return extract_pitch(loaded.waveform, sample_rate=loaded.sample_rate)


def test_detects_sa_from_synthetic_stable_pitch(tmp_path: Path) -> None:
    target_sa = 220.0
    frames = _extract_frames(tmp_path, target_sa)
    result = detect_sa(frames)

    assert isinstance(result, SaDetectionResult)
    assert result.sa_hz == pytest.approx(target_sa, rel=0.08)
    assert result.confidence >= config.SA_HISTOGRAM_MIN_PEAK_WEIGHT


def test_detects_sa_independently_for_two_scales(tmp_path: Path) -> None:
    guru_sa = 220.0
    disciple_sa = 330.0

    guru_frames = _extract_frames(tmp_path / "guru", guru_sa)
    disciple_frames = _extract_frames(tmp_path / "disciple", disciple_sa)

    guru_result = detect_sa(guru_frames)
    disciple_result = detect_sa(disciple_frames)

    assert guru_result.sa_hz == pytest.approx(guru_sa, rel=0.08)
    assert disciple_result.sa_hz == pytest.approx(disciple_sa, rel=0.08)
    assert guru_result.sa_hz != pytest.approx(disciple_result.sa_hz, rel=0.05)


def test_ignores_low_confidence_frames_for_sa_estimation() -> None:
    """Low-confidence frames must not drive Sa; high-confidence 220 Hz dominates."""
    frames: list[PitchFrame] = []
    for _ in range(60):
        frames.append(
            PitchFrame(
                time_seconds=0.0,
                frequency_hz=220.0,
                confidence=0.9,
                voiced=True,
                silent_or_unvoiced=False,
            )
        )
    for _ in range(60):
        frames.append(
            PitchFrame(
                time_seconds=0.0,
                frequency_hz=110.0,
                confidence=0.4,
                voiced=False,
                silent_or_unvoiced=False,
            )
        )

    result = detect_sa(frames)
    assert result.sa_hz == pytest.approx(220.0, rel=0.05)


def test_sa_detection_failed_when_insufficient_sa_frames() -> None:
    # Plot-level voiced count OK, but high-confidence Sa frames below minimum (30).
    frames = [
        PitchFrame(
            time_seconds=0.01 * index,
            frequency_hz=220.0,
            confidence=0.9,
            voiced=True,
            silent_or_unvoiced=False,
        )
        for index in range(29)
    ]
    frames.extend(
        PitchFrame(
            time_seconds=0.3 + 0.01 * index,
            frequency_hz=330.0,
            confidence=0.4,
            voiced=True,
            silent_or_unvoiced=False,
        )
        for index in range(6)
    )
    with pytest.raises(HcsaError) as exc_info:
        detect_sa(frames)
    assert exc_info.value.error_code == "sa_detection_failed"


def test_no_vocals_detected_when_too_few_voiced_frames() -> None:
    frames = [
        PitchFrame(
            time_seconds=0.01 * index,
            frequency_hz=None,
            confidence=0.1,
            voiced=False,
            silent_or_unvoiced=True,
        )
        for index in range(100)
    ]
    with pytest.raises(HcsaError) as exc_info:
        ensure_vocals_present(frames)
    assert exc_info.value.error_code == "no_vocals_detected"


def test_hz_to_cents_from_sa_octave_and_fifth() -> None:
    sa_hz = 220.0
    octave_hz = 440.0
    fifth_cents = 700.0
    fifth_hz = sa_hz * (2.0 ** (fifth_cents / 1200.0))

    assert hz_to_cents_from_sa(octave_hz, sa_hz) == pytest.approx(1200.0, abs=1.0)
    assert hz_to_cents_from_sa(fifth_hz, sa_hz) == pytest.approx(fifth_cents, abs=1.0)


def test_different_scales_normalize_to_same_relative_cents(tmp_path: Path) -> None:
    """Independent Sa per scale; same swara interval yields matching cents-from-Sa."""
    guru_sa_target = 220.0
    disciple_sa_target = 330.0
    pa_cents = 700.0

    guru_sa_detected = detect_sa(_extract_frames(tmp_path / "g_sa", guru_sa_target)).sa_hz
    disciple_sa_detected = detect_sa(
        _extract_frames(tmp_path / "d_sa", disciple_sa_target)
    ).sa_hz

    guru_pa_hz = guru_sa_detected * (2.0 ** (pa_cents / 1200.0))
    disciple_pa_hz = disciple_sa_detected * (2.0 ** (pa_cents / 1200.0))

    assert hz_to_cents_from_sa(guru_pa_hz, guru_sa_detected) == pytest.approx(pa_cents, abs=1.0)
    assert hz_to_cents_from_sa(disciple_pa_hz, disciple_sa_detected) == pytest.approx(
        pa_cents, abs=1.0
    )
    assert guru_sa_detected == pytest.approx(guru_sa_target, rel=0.08)
    assert disciple_sa_detected == pytest.approx(disciple_sa_target, rel=0.08)
