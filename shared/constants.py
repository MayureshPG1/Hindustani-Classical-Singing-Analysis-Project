"""Shared constants used by backend and frontend."""

from __future__ import annotations

API_HOST = "127.0.0.1"
API_PORT = 8765
API_VERSION = "v1"
API_BASE_URL = f"http://{API_HOST}:{API_PORT}/api/{API_VERSION}"

APP_VERSION = "0.1.0"

MAX_AUDIO_DURATION_SECONDS = 300  # 5 minutes per file
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a"}
