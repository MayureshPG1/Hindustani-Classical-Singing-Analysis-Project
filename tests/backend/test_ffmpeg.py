"""Tests for bundled FFmpeg resolution and decode."""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pytest

from backend.app.core.ffmpeg import (
    configure_ffmpeg,
    decode_mono_pcm,
    get_ffmpeg_executable,
    probe_audio,
)
from tests.fixtures.audio_factory import write_wav


@pytest.fixture(autouse=True)
def _reset_ffmpeg_cache() -> None:
    import backend.app.core.ffmpeg as ffmpeg_mod

    ffmpeg_mod._FFMPEG_EXE = None
    configure_ffmpeg()
    yield
    ffmpeg_mod._FFMPEG_EXE = None


def test_get_ffmpeg_executable_uses_imageio_bundle() -> None:
    exe = get_ffmpeg_executable()
    assert exe is not None
    assert Path(exe).exists()


def test_probe_and_decode_m4a(tmp_path: Path) -> None:
    ffmpeg = get_ffmpeg_executable()
    assert ffmpeg is not None

    source = write_wav(tmp_path / "tone.wav", duration_seconds=0.4, sample_rate=44100)
    m4a = tmp_path / "clip.m4a"
    subprocess.run(
        [ffmpeg, "-y", "-i", str(source), "-c:a", "aac", str(m4a)],
        check=True,
        capture_output=True,
    )

    probe = probe_audio(m4a)
    assert probe.duration_seconds == pytest.approx(0.4, rel=0.15)
    assert probe.sample_rate == 44100

    waveform = decode_mono_pcm(m4a, sample_rate=22050)
    assert waveform.ndim == 1
    assert len(waveform) == pytest.approx(int(0.4 * 22050), rel=0.1)
    assert float(np.max(np.abs(waveform))) > 0.01
