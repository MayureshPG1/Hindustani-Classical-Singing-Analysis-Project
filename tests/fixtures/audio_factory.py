"""Synthetic WAV fixtures for audio loader and API tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf


def write_wav(
    path: Path,
    *,
    duration_seconds: float,
    sample_rate: int = 44100,
    frequency_hz: float = 440.0,
    amplitude: float = 0.5,
    leading_silence_seconds: float = 0.0,
    trailing_silence_seconds: float = 0.0,
    channels: int = 1,
) -> Path:
    """Write a sine (or silence-only) WAV file."""
    tone_samples = max(int(duration_seconds * sample_rate), 0)
    lead = int(leading_silence_seconds * sample_rate)
    trail = int(trailing_silence_seconds * sample_rate)

    tone = np.zeros(tone_samples, dtype=np.float32)
    if frequency_hz > 0 and tone_samples > 0:
        t = np.arange(tone_samples, dtype=np.float32) / sample_rate
        tone = (amplitude * np.sin(2.0 * np.pi * frequency_hz * t)).astype(np.float32)

    mono = np.concatenate(
        [
            np.zeros(lead, dtype=np.float32),
            tone,
            np.zeros(trail, dtype=np.float32),
        ]
    )
    if channels == 1:
        data = mono
    else:
        data = np.column_stack([mono, mono * 0.8])

    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, data, sample_rate)
    return path


def write_silence_wav(path: Path, duration_seconds: float, sample_rate: int = 44100) -> Path:
    return write_wav(
        path,
        duration_seconds=duration_seconds,
        sample_rate=sample_rate,
        frequency_hz=0.0,
        amplitude=0.0,
    )
