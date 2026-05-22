"""Backend analysis and API configuration."""

from __future__ import annotations

from shared.constants import (
    API_HOST,
    API_PORT,
    MAX_AUDIO_DURATION_SECONDS,
)

# librosa.pyin
SR = 22050
HOP_LENGTH = 512
FRAME_LENGTH = 2048
FMIN_HZ = 50.0
FMAX_HZ = 1000.0

# Seconds of audio per pyin chunk when logging progress (verbose mode)
PYIN_CHUNK_SECONDS = 15.0

# Voiced / plot / compare
VOICED_PROB_PLOT_MIN = 0.55
VOICED_PROB_SILENT_MAX = 0.35

# Sa estimation
VOICED_PROB_SA_MIN = 0.65
SA_MIN_VOICED_FRAMES = 50
SA_MIN_VOICED_DURATION_SEC = 0.5
SA_HISTOGRAM_MIN_PEAK_WEIGHT = 0.15

# no_vocals_detected
MIN_VOICED_FRAMES_TOTAL = 30
MIN_VOICED_FRACTION = 0.05

# POST /audio/inspect pitch preview in response
INSPECT_PITCH_PREVIEW_FRAMES = 5

# Matched-portion discovery
MIN_WINDOW_SECONDS = 1.0
WINDOW_STEP_SECONDS = 0.25
MIN_VOICED_RATIO_IN_WINDOW = 0.40
MIN_VOICED_FRAMES_IN_WINDOW = 30
MATCH_RESAMPLE_LENGTH = 50
MATCH_CORRELATION_MIN = 0.70
MATCH_MACE_MAX_CENTS = 80.0
MATCH_NORMALIZED_DTW_MAX = 1.2
MATCH_MERGE_GAP_SECONDS = 0.5
MATCH_MIN_VOICED_FRACTION_OF_GURU = 0.20
MATCH_MIN_LONGEST_VOICED_SECONDS = 0.8

# Re-export for services
__all__ = [
    "API_HOST",
    "API_PORT",
    "MAX_AUDIO_DURATION_SECONDS",
    "SR",
    "HOP_LENGTH",
    "FRAME_LENGTH",
    "FMIN_HZ",
    "FMAX_HZ",
]
