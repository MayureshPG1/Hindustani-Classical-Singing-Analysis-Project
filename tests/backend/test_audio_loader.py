"""Unit tests for audio_loader."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from backend.app.core import config
from backend.app.core.errors import HcsaError
from backend.app.models.audio import ValidationStatus
from backend.app.services.audio_loader import load_and_validate
from tests.fixtures.audio_factory import write_silence_wav, write_wav


def test_loads_wav_and_returns_metadata(tmp_path: Path) -> None:
    path = write_wav(tmp_path / "tone.wav", duration_seconds=1.0, sample_rate=44100)
    loaded = load_and_validate(path, role="guru", file_name="tone.wav")

    assert loaded.file_info.validation_status == ValidationStatus.VALID
    assert loaded.file_info.format == "wav"
    assert loaded.file_info.channels == 1
    assert loaded.file_info.sample_rate == 44100
    assert 0.9 <= loaded.file_info.duration_seconds <= 1.1
    assert loaded.sample_rate == config.SR
    assert loaded.waveform.ndim == 1


def test_rejects_unsupported_extension(tmp_path: Path) -> None:
    path = tmp_path / "track.flac"
    path.write_bytes(b"fake")
    with pytest.raises(HcsaError) as exc_info:
        load_and_validate(path, role="guru", file_name="track.flac")
    assert exc_info.value.error_code == "unsupported_file_type"


def test_rejects_file_too_long(tmp_path: Path) -> None:
    path = write_wav(tmp_path / "long.wav", duration_seconds=301.0, sample_rate=22050)
    with pytest.raises(HcsaError) as exc_info:
        load_and_validate(path, role="guru", file_name="long.wav")
    assert exc_info.value.error_code == "file_too_long"
    assert exc_info.value.details["max_duration_seconds"] == 300


def test_stereo_converted_to_mono(tmp_path: Path) -> None:
    path = write_wav(
        tmp_path / "stereo.wav",
        duration_seconds=0.5,
        sample_rate=44100,
        channels=2,
    )
    loaded = load_and_validate(path, role="disciple", file_name="stereo.wav")
    assert loaded.file_info.channels == 2
    assert loaded.waveform.ndim == 1
    assert len(loaded.waveform) == pytest.approx(int(0.5 * config.SR), rel=0.05)


def test_preserves_leading_and_trailing_silence(tmp_path: Path) -> None:
    path = write_wav(
        tmp_path / "padded.wav",
        duration_seconds=0.5,
        sample_rate=44100,
        leading_silence_seconds=0.25,
        trailing_silence_seconds=0.25,
    )
    loaded = load_and_validate(path, role="guru", file_name="padded.wav")
    expected_samples = int(1.0 * config.SR)
    assert len(loaded.waveform) == pytest.approx(expected_samples, rel=0.05)
    assert float(np.max(np.abs(loaded.waveform[: int(0.2 * config.SR)]))) < 1e-6


def test_resamples_to_analysis_rate(tmp_path: Path) -> None:
    path = write_wav(tmp_path / "highsr.wav", duration_seconds=2.0, sample_rate=48000)
    loaded = load_and_validate(path, role="guru", file_name="highsr.wav")
    assert loaded.sample_rate == config.SR
    assert loaded.file_info.duration_seconds == pytest.approx(2.0, rel=0.05)


def test_no_audio_detected_for_silence_only(tmp_path: Path) -> None:
    path = write_silence_wav(tmp_path / "silent.wav", duration_seconds=1.0)
    with pytest.raises(HcsaError) as exc_info:
        load_and_validate(path, role="guru", file_name="silent.wav")
    assert exc_info.value.error_code == "no_audio_detected"


def test_decode_failed_for_corrupt_file(tmp_path: Path) -> None:
    path = tmp_path / "bad.wav"
    path.write_bytes(b"not a wav file")
    with pytest.raises(HcsaError) as exc_info:
        load_and_validate(path, role="guru", file_name="bad.wav")
    assert exc_info.value.error_code == "decode_failed"


def test_loads_mp3_if_decoder_available(tmp_path: Path) -> None:
    pytest.importorskip("audioread")
    import shutil

    # Build a minimal mp3 via external tool if missing; skip when unavailable.
    source = tmp_path / "tone.wav"
    write_wav(source, duration_seconds=0.5)
    target = tmp_path / "tone.mp3"
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        pytest.skip("ffmpeg not available for MP3 fixture")
    import subprocess

    subprocess.run(
        [ffmpeg, "-y", "-i", str(source), str(target)],
        check=True,
        capture_output=True,
    )
    loaded = load_and_validate(target, role="guru", file_name="tone.mp3")
    assert loaded.file_info.format == "mp3"
    assert loaded.file_info.validation_status == ValidationStatus.VALID


def test_loads_m4a_if_decoder_available(tmp_path: Path) -> None:
    pytest.importorskip("audioread")
    import shutil
    import subprocess

    source = tmp_path / "tone.wav"
    write_wav(source, duration_seconds=0.5)
    target = tmp_path / "tone.m4a"
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        pytest.skip("ffmpeg not available for M4A fixture")
    subprocess.run(
        [ffmpeg, "-y", "-i", str(source), "-c:a", "aac", str(target)],
        check=True,
        capture_output=True,
    )
    loaded = load_and_validate(target, role="guru", file_name="tone.m4a")
    assert loaded.file_info.format == "m4a"
    assert loaded.file_info.validation_status == ValidationStatus.VALID
