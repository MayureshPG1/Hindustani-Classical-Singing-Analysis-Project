"""Pitch frame models shared by inspect and compare."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PitchFrame(BaseModel):
    """Pitch analysis for one time frame."""

    time_seconds: float
    frequency_hz: float | None = None
    confidence: float | None = None
    voiced: bool
    silent_or_unvoiced: bool


class PitchSummary(BaseModel):
    """Lightweight voiced-frame stats for one recording."""

    voiced_frame_count: int
    total_frame_count: int
    voiced_fraction: float
