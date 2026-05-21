"""Load and validate audio files with librosa (no silence trimming)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from backend.app.core import config
from backend.app.core.errors import (
    HcsaError,
    raise_decode_failed,
    raise_file_too_long,
    raise_no_audio_detected,
    raise_unsupported_file_type,
)
from backend.app.models.audio import AudioFileInfo, ValidationStatus
from shared.constants import MAX_AUDIO_DURATION_SECONDS, SUPPORTED_AUDIO_EXTENSIONS

# Peak below this after decode is treated as empty audio.
_MIN_PEAK_AMPLITUDE = 1e-8


@dataclass
class LoadedAudio:
    """Decoded mono waveform at analysis sample rate."""

    waveform: np.ndarray
    sample_rate: int
    path: Path
    file_info: AudioFileInfo


def normalize_extension(file_name: str) -> str:
    return Path(file_name).suffix.lower()


def is_supported_file_name(file_name: str) -> bool:
    return normalize_extension(file_name) in SUPPORTED_AUDIO_EXTENSIONS


def make_file_id(role: str) -> str:
    return f"{role}-{uuid.uuid4().hex[:8]}"


def load_and_validate(
    path: Path,
    *,
    role: str,
    file_name: str,
    file_id: str | None = None,
) -> LoadedAudio:
    """
    Load audio with librosa (mono, SR=22050), validate duration and content.

    Preserves the full timeline; does not trim silence.
    """
    if not is_supported_file_name(file_name):
        raise_unsupported_file_type(file_name)

    resolved_id = file_id or make_file_id(role)
    native_sr: int | None = None
    native_channels = 1

    try:
        info = sf.info(path)
        native_sr = info.samplerate
        native_channels = info.channels
        if info.duration > MAX_AUDIO_DURATION_SECONDS:
            raise_file_too_long(float(info.duration))
    except HcsaError:
        raise
    except Exception:
        native_sr = None

    try:
        waveform, sr = librosa.load(
            path,
            sr=config.SR,
            mono=True,
            duration=None,
        )
    except Exception as exc:
        raise_decode_failed(file_name, str(exc))

    duration_seconds = float(len(waveform) / sr) if sr else 0.0
    if duration_seconds > MAX_AUDIO_DURATION_SECONDS:
        raise_file_too_long(duration_seconds)

    if waveform.size == 0 or float(np.max(np.abs(waveform))) < _MIN_PEAK_AMPLITUDE:
        raise_no_audio_detected()

    audio_format = normalize_extension(file_name).lstrip(".")
    file_info = AudioFileInfo(
        file_id=resolved_id,
        file_name=file_name,
        duration_seconds=round(duration_seconds, 3),
        sample_rate=native_sr or sr,
        channels=native_channels,
        format=audio_format,
        validation_status=ValidationStatus.VALID,
        error_message=None,
    )
    return LoadedAudio(
        waveform=waveform,
        sample_rate=sr,
        path=path,
        file_info=file_info,
    )
