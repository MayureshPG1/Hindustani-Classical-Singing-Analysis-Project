"""Domain exceptions and API error code mapping."""

from __future__ import annotations

from shared.constants import (
    MAX_AUDIO_DURATION_SECONDS,
    MAX_TOLERANCE_CENTS,
    MIN_TOLERANCE_CENTS,
)

UNSUPPORTED_FILE_TYPE_MESSAGE = "File type is not supported. Use WAV, MP3, or M4A."
FILE_TOO_LONG_MESSAGE = "Audio file must be 5 minutes or shorter."
NO_AUDIO_DETECTED_MESSAGE = "No usable audio was detected in this file."
DECODE_FAILED_MESSAGE = "The audio file could not be decoded."
NO_VOCALS_DETECTED_MESSAGE = (
    "No reliable vocal pitch was detected. Try a clearer vocal recording."
)
INVALID_TOLERANCE_MESSAGE = "Tolerance must be between 0 and 25 cents."
COMPARISON_FAILED_MESSAGE = (
    "Comparison could not be scored. No overlapping voiced pitch was found."
)


class HcsaError(Exception):
    """Base error for analysis and validation failures."""

    def __init__(self, error_code: str, message: str, details: dict | None = None) -> None:
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)


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


def raise_no_vocals_detected(*, role: str, summary: object | None = None) -> None:
    details: dict[str, object] = {"role": role}
    if summary is not None:
        if hasattr(summary, "model_dump"):
            details["pitch_summary"] = summary.model_dump()
        else:
            details["pitch_summary"] = summary
    raise HcsaError("no_vocals_detected", NO_VOCALS_DETECTED_MESSAGE, details)


def raise_invalid_tolerance(tolerance_cents: int) -> None:
    raise HcsaError(
        "invalid_tolerance",
        INVALID_TOLERANCE_MESSAGE,
        {
            "tolerance_cents": tolerance_cents,
            "min_tolerance_cents": MIN_TOLERANCE_CENTS,
            "max_tolerance_cents": MAX_TOLERANCE_CENTS,
        },
    )


def raise_comparison_failed(reason: str | None = None) -> None:
    details: dict[str, str] = {}
    if reason:
        details["reason"] = reason
    raise HcsaError("comparison_failed", COMPARISON_FAILED_MESSAGE, details)
