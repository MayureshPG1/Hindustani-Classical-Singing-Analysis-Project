"""Client-side upload validation tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from frontend.validation import FILE_TOO_LONG_MESSAGE, read_duration_seconds, validate_upload_path
from tests.fixtures.audio_factory import write_wav


def test_validate_rejects_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.wav"
    assert validate_upload_path(missing) is not None


def test_validate_rejects_empty_file(tmp_path: Path) -> None:
    empty = tmp_path / "empty.wav"
    empty.write_bytes(b"")
    assert validate_upload_path(empty) is not None


def test_validate_rejects_unsupported_extension(tmp_path: Path) -> None:
    bad = tmp_path / "track.flac"
    bad.write_bytes(b"\x00\x01")
    message = validate_upload_path(bad)
    assert message is not None
    assert ".flac" not in message or "Unsupported" in message


def test_validate_rejects_wav_longer_than_five_minutes(tmp_path: Path) -> None:
    long_wav = write_wav(tmp_path / "long.wav", duration_seconds=301.0, sample_rate=22050)
    assert validate_upload_path(long_wav) == FILE_TOO_LONG_MESSAGE


def test_validate_accepts_short_wav(tmp_path: Path) -> None:
    wav = write_wav(tmp_path / "tone.wav", duration_seconds=1.0)
    assert validate_upload_path(wav) is None


def test_read_duration_seconds_for_wav(tmp_path: Path) -> None:
    wav = write_wav(tmp_path / "tone.wav", duration_seconds=1.5)
    duration = read_duration_seconds(wav)
    assert duration is not None
    assert 1.0 <= duration <= 1.6
