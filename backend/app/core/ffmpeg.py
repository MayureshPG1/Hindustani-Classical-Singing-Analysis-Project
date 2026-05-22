"""FFmpeg resolution and decode helpers for compressed audio (MP3, M4A)."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_FFMPEG_EXE: str | None = None
_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d{2}):(\d{2}\.?\d*)")
_AUDIO_STREAM_RE = re.compile(r"(\d+)\s*Hz,\s*(mono|stereo)\b", re.IGNORECASE)


def _subprocess_kwargs() -> dict:
    if sys.platform == "win32":
        return {"creationflags": 0x08000000}
    return {}


def get_ffmpeg_executable() -> str | None:
    """Return system FFmpeg on PATH, else the bundled imageio-ffmpeg binary."""
    global _FFMPEG_EXE
    if _FFMPEG_EXE is not None:
        return _FFMPEG_EXE or None

    import shutil

    system = shutil.which("ffmpeg")
    if system:
        _FFMPEG_EXE = system
        return _FFMPEG_EXE

    try:
        import imageio_ffmpeg

        _FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        _FFMPEG_EXE = ""
    return _FFMPEG_EXE or None


def configure_ffmpeg() -> str | None:
    """Resolve FFmpeg once at app startup."""
    return get_ffmpeg_executable()


@dataclass(frozen=True)
class FfmpegAudioProbe:
    duration_seconds: float | None
    sample_rate: int | None
    channels: int | None


def _parse_duration(stderr: str) -> float | None:
    match = _DURATION_RE.search(stderr)
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _parse_audio_stream(stderr: str) -> tuple[int | None, int | None]:
    match = _AUDIO_STREAM_RE.search(stderr)
    if not match:
        return None, None
    sample_rate = int(match.group(1))
    layout = match.group(2).lower()
    channels = 1 if layout == "mono" else 2
    return sample_rate, channels


def probe_audio(path: Path) -> FfmpegAudioProbe:
    """Read duration and stream metadata via `ffmpeg -i` (stderr)."""
    ffmpeg = get_ffmpeg_executable()
    if ffmpeg is None:
        return FfmpegAudioProbe(None, None, None)

    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        **_subprocess_kwargs(),
    )
    stderr = proc.stderr or ""
    sample_rate, channels = _parse_audio_stream(stderr)
    return FfmpegAudioProbe(
        duration_seconds=_parse_duration(stderr),
        sample_rate=sample_rate,
        channels=channels,
    )


def decode_mono_pcm(path: Path, *, sample_rate: int) -> np.ndarray:
    """Decode file to mono float32 PCM at the given sample rate."""
    ffmpeg = get_ffmpeg_executable()
    if ffmpeg is None:
        raise RuntimeError("FFmpeg is not available for decoding compressed audio.")

    cmd = [
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-f",
        "f32le",
        "-acodec",
        "pcm_f32le",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-",
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        **_subprocess_kwargs(),
    )
    if proc.returncode != 0 or not proc.stdout:
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        detail = stderr[-500:] if stderr else f"ffmpeg exited with code {proc.returncode}"
        raise RuntimeError(detail)
    return np.frombuffer(proc.stdout, dtype=np.float32).copy()
