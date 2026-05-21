"""Domain exceptions and API error code mapping."""

from __future__ import annotations

import math
from typing import Any

from shared.constants import (
    MAX_AUDIO_DURATION_SECONDS,
    MAX_TOLERANCE_CENTS,
    MIN_TOLERANCE_CENTS,
)

INVALID_TOLERANCE_MESSAGE = (
    "Tolerance must be numeric and within the allowed range."
)
UNSUPPORTED_FILE_TYPE_MESSAGE = "File type is not supported. Use WAV or MP3 only."
FILE_TOO_LONG_MESSAGE = "Audio file must be 2 minutes or shorter."
NO_AUDIO_DETECTED_MESSAGE = "No usable audio was detected in this file."
DECODE_FAILED_MESSAGE = "The audio file could not be decoded."


class HcsaError(Exception):
    """Base error for analysis and validation failures."""

    def __init__(self, error_code: str, message: str, details: dict | None = None) -> None:
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def validate_tolerance_cents(value: Any) -> float:
    """Validate tolerance for PUT /settings/tolerance."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise HcsaError(
            "invalid_tolerance",
            INVALID_TOLERANCE_MESSAGE,
            {"tolerance_cents": value},
        )
    numeric = float(value)
    if not math.isfinite(numeric):
        raise HcsaError(
            "invalid_tolerance",
            INVALID_TOLERANCE_MESSAGE,
            {"tolerance_cents": value},
        )
    if numeric < MIN_TOLERANCE_CENTS or numeric > MAX_TOLERANCE_CENTS:
        raise HcsaError(
            "invalid_tolerance",
            INVALID_TOLERANCE_MESSAGE,
            {"tolerance_cents": value},
        )
    return numeric


def raise_unsupported_file_type(file_name: str) -> None:
    raise HcsaError(
        "unsupported_file_type",
        UNSUPPORTED_FILE_TYPE_MESSAGE,
        {"file_name": file_name},
    )


def raise_file_too_long(duration_seconds: float) -> None:
    raise HcsaError(
        "file_too_long",
        FILE_TOO_LONG_MESSAGE,
        {
            "duration_seconds": duration_seconds,
            "max_duration_seconds": MAX_AUDIO_DURATION_SECONDS,
        },
    )


def raise_no_audio_detected() -> None:
    raise HcsaError("no_audio_detected", NO_AUDIO_DETECTED_MESSAGE)


def raise_decode_failed(file_name: str, reason: str | None = None) -> None:
    details: dict[str, str] = {"file_name": file_name}
    if reason:
        details["reason"] = reason
    raise HcsaError("decode_failed", DECODE_FAILED_MESSAGE, details)
