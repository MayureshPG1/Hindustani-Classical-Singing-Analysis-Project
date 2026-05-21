"""Audio file metadata models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ValidationStatus(str, Enum):
    """Upload / inspect validation state."""

    EMPTY = "empty"
    LOADING = "loading"
    VALID = "valid"
    INVALID = "invalid"


class AudioFileInfo(BaseModel):
    """File metadata after upload or validation."""

    file_id: str
    file_name: str
    duration_seconds: float
    sample_rate: int
    channels: int
    format: str
    validation_status: ValidationStatus
    error_message: str | None = None
