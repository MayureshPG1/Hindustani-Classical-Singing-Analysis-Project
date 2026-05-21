"""Shared constants used by backend and frontend."""

from __future__ import annotations

API_HOST = "127.0.0.1"
API_PORT = 8765
API_VERSION = "v1"
API_BASE_URL = f"http://{API_HOST}:{API_PORT}/api/{API_VERSION}"

APP_VERSION = "0.1.0"

MAX_AUDIO_DURATION_SECONDS = 300  # 5 minutes per file
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3"}

DEFAULT_TOLERANCE_CENTS = 0.0
MIN_TOLERANCE_CENTS = 0.0
MAX_TOLERANCE_CENTS = 25.0
TOLERANCE_STEP_CENTS = 5.0

SWARA_TABLE: list[dict[str, str | float]] = [
    {"label": "Sa", "symbol": "S", "cents_from_sa": 0},
    {"label": "Komal Re", "symbol": "r", "cents_from_sa": 100},
    {"label": "Shuddha Re", "symbol": "R", "cents_from_sa": 200},
    {"label": "Komal Ga", "symbol": "g", "cents_from_sa": 300},
    {"label": "Shuddha Ga", "symbol": "G", "cents_from_sa": 400},
    {"label": "Shuddha Ma", "symbol": "m", "cents_from_sa": 500},
    {"label": "Tivra Ma", "symbol": "M", "cents_from_sa": 600},
    {"label": "Pa", "symbol": "P", "cents_from_sa": 700},
    {"label": "Komal Dha", "symbol": "d", "cents_from_sa": 800},
    {"label": "Shuddha Dha", "symbol": "D", "cents_from_sa": 900},
    {"label": "Komal Ni", "symbol": "n", "cents_from_sa": 1000},
    {"label": "Shuddha Ni", "symbol": "N", "cents_from_sa": 1100},
]
