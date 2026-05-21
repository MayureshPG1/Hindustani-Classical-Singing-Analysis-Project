"""Comparison and session API models (minimal pitch-overlay MVP)."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from backend.app.models.audio import AudioFileInfo
from backend.app.models.pitch import PitchFrame, PitchSummary


class ProcessingStatus(str, Enum):
    """Backend comparison pipeline state."""

    IDLE = "idle"
    LOADING_AUDIO = "loading_audio"
    EXTRACTING_PITCH = "extracting_pitch"
    GENERATING_GRAPH = "generating_graph"
    COMPLETE = "complete"
    ERROR = "error"


class ClearSessionResponse(BaseModel):
    """Response for POST /session/clear."""

    status: str = "cleared"


class HealthResponse(BaseModel):
    """Response for GET /health."""

    status: str
    version: str


class ComparisonResult(BaseModel):
    """Top-level compare API response."""

    guru_file_info: AudioFileInfo
    disciple_file_info: AudioFileInfo
    guru_pitch_frames: list[PitchFrame] = Field(default_factory=list)
    disciple_pitch_frames: list[PitchFrame] = Field(default_factory=list)
    guru_summary: PitchSummary | None = None
    disciple_summary: PitchSummary | None = None
    warnings: list[str] = Field(default_factory=list)
