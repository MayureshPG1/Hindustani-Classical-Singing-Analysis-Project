"""Shared constants used by backend and frontend."""

from __future__ import annotations

API_HOST = "127.0.0.1"
API_PORT = 8765
API_VERSION = "v1"
API_BASE_URL = f"http://{API_HOST}:{API_PORT}/api/{API_VERSION}"

APP_VERSION = "0.1.0"

MAX_AUDIO_DURATION_SECONDS = 300  # 5 minutes per file
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a"}

MIN_TOLERANCE_CENTS = 0
MAX_TOLERANCE_CENTS = 25
DEFAULT_TOLERANCE_CENTS = 0

# Equal-tempered swara reference frequencies (Hz) for graph Y-axis labels.
SWARA_FREQUENCIES_HZ: dict[str, float] = {
    "'S": 130.81,
    "'r": 138.59,
    "'R": 146.83,
    "'g": 155.56,
    "'G": 164.81,
    "'m": 174.61,
    "'M": 185.00,
    "'P": 196.00,
    "'d": 207.65,
    "'D": 220.00,
    "'n": 233.08,
    "'N": 246.94,
    "S": 261.63,
    "r": 277.18,
    "R": 293.66,
    "g": 311.13,
    "G": 329.63,
    "m": 349.23,
    "M": 369.99,
    "P": 392.00,
    "d": 415.30,
    "D": 440.00,
    "n": 466.16,
    "N": 493.88,
    "S'": 523.25,
    "r'": 554.37,
    "R'": 587.33,
    "g'": 622.25,
    "G'": 659.26,
    "m'": 698.46,
    "M'": 739.99,
    "P'": 783.99,
    "d'": 830.61,
    "D'": 880.00,
    "n'": 932.33,
    "N'": 987.77,
}

# Fully visible pitch graph Y-axis (covers all swara reference frequencies).
PITCH_GRAPH_Y_MIN_HZ = 130.0
PITCH_GRAPH_Y_MAX_HZ = 988.0

SWARA_Y_AXIS_TICKS: tuple[tuple[float, str], ...] = tuple(
    (hz, name)
    for name, hz in sorted(SWARA_FREQUENCIES_HZ.items(), key=lambda item: item[1])
)
