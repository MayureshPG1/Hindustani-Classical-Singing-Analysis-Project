"""Comparison and session API models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from backend.app.models.audio import AudioFileInfo


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


class ComparisonSummary(BaseModel):
    """Wall-clock Hz comparison metrics (no Sa / DTW in v1)."""

    overall_score: float = Field(description="Match share of scored frame pairs (0–100).")
    average_deviation_cents: float
    match_percentage: float
    higher_percentage: float
    lower_percentage: float
    tolerance_cents: int = Field(description="Tolerance used for match/higher/lower.")


class ComparisonResult(BaseModel):
    """Top-level compare API response."""

    guru_file_info: AudioFileInfo
    disciple_file_info: AudioFileInfo
    comparison_summary: ComparisonSummary
