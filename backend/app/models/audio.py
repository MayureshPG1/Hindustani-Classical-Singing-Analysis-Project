"""Audio file metadata and inspect response models."""

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


class PitchMetadata(BaseModel):
    """Full-timeline voiced-frame stats from inspect pitch extraction."""

    voiced_frame_count: int
    total_frame_count: int
    voiced_fraction: float


class AudioInspectResponse(BaseModel):
    """Response for POST /audio/inspect."""

    file_info: AudioFileInfo
    pitch_metadata: PitchMetadata
