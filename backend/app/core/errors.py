"""Domain exceptions and API error code mapping."""

from __future__ import annotations

import math
from typing import Any

from shared.constants import MAX_TOLERANCE_CENTS, MIN_TOLERANCE_CENTS

INVALID_TOLERANCE_MESSAGE = (
    "Tolerance must be numeric and within the allowed range."
)


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
