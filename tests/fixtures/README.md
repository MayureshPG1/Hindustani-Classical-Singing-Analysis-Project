# Test fixtures

`audio_factory.py` provides synthetic WAV helpers for loader and API tests. Compressed-format tests (MP3, M4A) build fixtures with `ffmpeg` when available.

Do not add `tests/backend/__init__.py` — it shadows the project `backend` package.
