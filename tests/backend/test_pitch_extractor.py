"""Unit tests for pitch_extractor."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from backend.app.core import config
from backend.app.core.errors import HcsaError
from backend.app.models.comparison import PitchFrame
from backend.app.services.audio_loader import load_and_validate
from backend.app.services.pitch_extractor import extract_pitch
from tests.fixtures.audio_factory import write_silence_wav, write_wav


def _expected_frame_count(num_samples: int) -> int:
    """Match librosa.pyin frame count for the configured hop length."""
    return int(np.ceil(num_samples / config.HOP_LENGTH))


def test_extracts_f0_from_synthetic_sine_wave(tmp_path: Path) -> None:
    frequency_hz = 220.0
    path = write_wav(
        tmp_path / "sine.wav",
        duration_seconds=2.0,
        sample_rate=config.SR,
        frequency_hz=frequency_hz,
        amplitude=0.6,
    )
    loaded = load_and_validate(path, role="guru", file_name="sine.wav")
    frames = extract_pitch(loaded.waveform, sample_rate=loaded.sample_rate)

    assert len(frames) == _expected_frame_count(len(loaded.waveform))
    voiced = [f for f in frames if f.voiced and f.frequency_hz is not None]
    assert len(voiced) >= config.MIN_VOICED_FRAMES_TOTAL

    median_f0 = float(np.median([f.frequency_hz for f in voiced]))
    assert median_f0 == pytest.approx(frequency_hz, rel=0.08)


def test_marks_silent_region_as_unvoiced(tmp_path: Path) -> None:
    path = write_wav(
        tmp_path / "padded.wav",
        duration_seconds=0.6,
        sample_rate=config.SR,
        frequency_hz=330.0,
        amplitude=0.6,
        leading_silence_seconds=0.3,
        trailing_silence_seconds=0.3,
    )
    loaded = load_and_validate(path, role="guru", file_name="padded.wav")
    frames = extract_pitch(loaded.waveform, sample_rate=loaded.sample_rate)

    assert len(frames) == _expected_frame_count(len(loaded.waveform))

    lead_frames = [f for f in frames if f.time_seconds < 0.28]
    trail_frames = [f for f in frames if f.time_seconds > 1.0]
    assert lead_frames
    assert trail_frames
    assert all(not f.voiced for f in lead_frames + trail_frames)
    lead_silent = sum(1 for f in lead_frames if f.silent_or_unvoiced)
    trail_silent = sum(1 for f in trail_frames if f.silent_or_unvoiced)
    assert lead_silent / len(lead_frames) >= 0.85
    assert trail_silent / len(trail_frames) >= 0.85
    tone_frames = [f for f in frames if 0.32 <= f.time_seconds <= 0.88]
    assert any(f.voiced for f in tone_frames)


def test_preserves_frame_count_across_silence() -> None:
    sr = config.SR
    lead = int(0.4 * sr)
    tone = int(0.4 * sr)
    trail = int(0.4 * sr)
    t = np.arange(tone, dtype=np.float32) / sr
    waveform = np.concatenate(
        [
            np.zeros(lead, dtype=np.float32),
            (0.5 * np.sin(2.0 * np.pi * 261.63 * t)).astype(np.float32),
            np.zeros(trail, dtype=np.float32),
        ]
    )

    frames = extract_pitch(waveform, sample_rate=sr)
    assert len(frames) == _expected_frame_count(len(waveform))
    assert frames[0].time_seconds == pytest.approx(0.0, abs=0.02)
    last_time = (len(waveform) - 1) / sr
    assert frames[-1].time_seconds <= last_time


def test_returns_confidence_per_frame(tmp_path: Path) -> None:
    path = write_wav(
        tmp_path / "tone.wav",
        duration_seconds=1.0,
        sample_rate=config.SR,
        frequency_hz=440.0,
    )
    loaded = load_and_validate(path, role="guru", file_name="tone.wav")
    frames = extract_pitch(loaded.waveform, sample_rate=loaded.sample_rate)

    assert frames
    assert all(f.confidence is not None for f in frames)
    assert all(0.0 <= f.confidence <= 1.0 for f in frames)
    voiced = [f for f in frames if f.voiced]
    assert voiced
    assert all(f.confidence >= config.VOICED_PROB_PLOT_MIN for f in voiced)


def test_handles_no_pitch_audio_without_crash() -> None:
    sr = config.SR
    duration_samples = int(1.5 * sr)
    waveform = np.zeros(duration_samples, dtype=np.float32)
    waveform += np.random.default_rng(0).normal(0.0, 1e-6, size=duration_samples).astype(
        np.float32
    )

    frames = extract_pitch(waveform, sample_rate=sr)

    assert len(frames) == _expected_frame_count(len(waveform))
    assert all(isinstance(f, PitchFrame) for f in frames)
    assert not any(f.voiced for f in frames)


def test_silence_wav_fixture_still_extracts_frames_when_given_waveform() -> None:
    """Pitch extractor alone does not reject silence; loader does."""
    sr = config.SR
    waveform = np.zeros(int(sr), dtype=np.float32)
    frames = extract_pitch(waveform, sample_rate=sr)
    assert len(frames) > 0
    assert all(f.silent_or_unvoiced for f in frames)


def test_integration_with_loaded_padded_wav(tmp_path: Path) -> None:
    path = write_silence_wav(tmp_path / "silent.wav", duration_seconds=0.5, sample_rate=44100)
    with pytest.raises(HcsaError):
        load_and_validate(path, role="guru", file_name="silent.wav")

    path = write_wav(
        tmp_path / "phrase.wav",
        duration_seconds=1.0,
        sample_rate=44100,
        leading_silence_seconds=0.2,
        trailing_silence_seconds=0.2,
    )
    loaded = load_and_validate(path, role="disciple", file_name="phrase.wav")
    frames = extract_pitch(loaded.waveform, sample_rate=loaded.sample_rate)
    assert len(frames) == _expected_frame_count(len(loaded.waveform))
