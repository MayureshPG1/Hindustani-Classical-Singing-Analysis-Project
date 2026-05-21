"""Domain exceptions and API error code mapping (Phase 1+)."""

from __future__ import annotations


class HcsaError(Exception):
    """Base error for analysis and validation failures."""

    def __init__(self, error_code: str, message: str, details: dict | None = None) -> None:
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)
