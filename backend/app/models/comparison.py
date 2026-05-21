"""Comparison, tolerance, and session models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from backend.app.models.audio import AudioFileInfo


class ProcessingStatus(str, Enum):
    """Backend comparison pipeline state."""

    IDLE = "idle"
    LOADING_AUDIO = "loading_audio"
    EXTRACTING_PITCH = "extracting_pitch"
    DETECTING_SA = "detecting_sa"
    FINDING_MATCHING_PORTIONS = "finding_matching_portions"
    ALIGNING = "aligning"
    CALCULATING_COMPARISON = "calculating_comparison"
    GENERATING_GRAPH = "generating_graph"
    COMPLETE = "complete"
    ERROR = "error"


class FrameClassification(str, Enum):
    """Per-frame guru vs disciple pitch relation."""

    MATCH = "match"
    HIGHER = "higher"
    LOWER = "lower"
    UNKNOWN = "unknown"


class ExclusionReason(str, Enum):
    """Why a source time range was excluded from comparison."""

    NO_MATCHING_COUNTERPART = "no_matching_counterpart"
    SILENCE_OR_UNVOICED = "silence_or_unvoiced"
    LOW_CONFIDENCE = "low_confidence"
    OUTSIDE_MATCHED_REGION = "outside_matched_region"


class ToleranceSettings(BaseModel):
    """Current tolerance configuration."""

    tolerance_cents: float
    default_tolerance_cents: float = 0.0
    step_cents: float = 5.0
    minimum_tolerance_cents: float = 0.0
    maximum_tolerance_cents: float = 25.0


class ToleranceUpdateRequest(BaseModel):
    """Body for PUT /settings/tolerance."""

    tolerance_cents: float


class ClearSessionResponse(BaseModel):
    """Response for POST /session/clear."""

    status: str = "cleared"


class HealthResponse(BaseModel):
    """Response for GET /health."""

    status: str
    version: str


class TimeRange(BaseModel):
    """Inclusive time range in one recording."""

    start_seconds: float
    end_seconds: float


class ExcludedRange(BaseModel):
    """Portion of a recording left out of comparison."""

    source: str
    start_seconds: float
    end_seconds: float
    reason: ExclusionReason


class MatchedSegment(BaseModel):
    """Similar portion between guru and disciple."""

    segment_id: str
    guru_range: TimeRange
    disciple_range: TimeRange
    similarity_score: float | None = None


class PitchFrame(BaseModel):
    """Pitch analysis for one time frame."""

    time_seconds: float
    frequency_hz: float | None = None
    confidence: float | None = None
    voiced: bool
    silent_or_unvoiced: bool
    cents_from_sa: float | None = None
    sa_f0_hz: float | None = None
    swara_label: str | None = None
    swara_symbol: str | None = None
    swara_f0_hz: float | None = None


class SaDetectionMetadata(BaseModel):
    """Detected Sa (tonic) for one recording."""

    sa_hz: float
    confidence: float


class AudioInspectResponse(BaseModel):
    """Response for POST /audio/inspect."""

    file_info: AudioFileInfo
    sa: SaDetectionMetadata
    pitch_frames: list[PitchFrame] = Field(default_factory=list)


class ComparisonFrame(BaseModel):
    """One aligned comparison point."""

    aligned_time: float
    original_guru_time: float | None = None
    original_disciple_time: float | None = None
    guru_cents_from_sa: float | None = None
    disciple_cents_from_sa: float | None = None
    guru_sa_f0_hz: float | None = None
    disciple_sa_f0_hz: float | None = None
    guru_swara_label: str | None = None
    guru_swara_symbol: str | None = None
    guru_swara_f0_hz: float | None = None
    disciple_swara_label: str | None = None
    disciple_swara_symbol: str | None = None
    disciple_swara_f0_hz: float | None = None
    difference_cents: float | None = None
    classification: FrameClassification


class ComparisonMetrics(BaseModel):
    """Summary statistics for a comparison."""

    overall_score: float
    average_deviation_cents: float
    match_percentage: float
    higher_percentage: float
    lower_percentage: float
    unknown_percentage: float
    comparable_frame_count: int
    matched_frame_count: int
    excluded_frame_count: int
    total_frame_count: int
    total_matching_intervals: int | None = None
    total_intervals: int | None = None


class ComparisonResult(BaseModel):
    """Top-level compare API response."""

    guru_file_info: AudioFileInfo
    disciple_file_info: AudioFileInfo
    guru_sa_hz: float | None = None
    disciple_sa_hz: float | None = None
    tolerance_cents: float
    guru_pitch_frames: list[PitchFrame] = Field(default_factory=list)
    disciple_pitch_frames: list[PitchFrame] = Field(default_factory=list)
    matched_segments: list[MatchedSegment] = Field(default_factory=list)
    excluded_guru_ranges: list[ExcludedRange] = Field(default_factory=list)
    excluded_disciple_ranges: list[ExcludedRange] = Field(default_factory=list)
    aligned_frames: list[ComparisonFrame] = Field(default_factory=list)
    metrics: ComparisonMetrics
    warnings: list[str] = Field(default_factory=list)
