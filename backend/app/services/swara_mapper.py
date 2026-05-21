"""Map cents-from-Sa to swara labels (Phase 4)."""

from __future__ import annotations

import numpy as np

from backend.app.models.comparison import PitchFrame
from backend.app.models.swara import Swara
from backend.app.services.sa_detector import SaDetectionResult, detect_sa, hz_to_cents_from_sa
from shared.constants import SWARA_TABLE

SWARA_ENTRIES: list[Swara] = [Swara(**entry) for entry in SWARA_TABLE]


def get_swara_table() -> list[Swara]:
    """Return the fixed MVP swara mapping table."""
    return list(SWARA_ENTRIES)


def map_cents_to_swara(cents_from_sa: float) -> Swara:
    """Map cents relative to Sa to the nearest 100-cent swara bin."""
    wrapped = float(cents_from_sa) % 1200.0
    centers = np.array([entry.cents_from_sa for entry in SWARA_ENTRIES], dtype=np.float64)
    distances = np.abs(centers - wrapped)
    distances = np.minimum(distances, 1200.0 - distances)
    nearest = int(np.argmin(distances))
    return SWARA_ENTRIES[nearest]


def swara_f0_hz(sa_hz: float, swara_cents_from_sa: float) -> float:
    """Expected Hz of a swara given detected Sa."""
    return float(sa_hz * (2.0 ** (swara_cents_from_sa / 1200.0)))


def annotate_pitch_frames(
    frames: list[PitchFrame],
    sa_hz: float,
) -> list[PitchFrame]:
    """
    Attach Sa-relative cents and swara labels to each frame.

    Unvoiced frames keep pitch/swara fields unset but receive sa_f0_hz.
    """
    annotated: list[PitchFrame] = []
    for frame in frames:
        updates: dict[str, object] = {"sa_f0_hz": sa_hz}
        if frame.frequency_hz is not None and frame.voiced:
            cents = hz_to_cents_from_sa(frame.frequency_hz, sa_hz)
            swara = map_cents_to_swara(cents)
            updates["cents_from_sa"] = cents
            updates["swara_label"] = swara.label
            updates["swara_symbol"] = swara.symbol
            updates["swara_f0_hz"] = swara_f0_hz(sa_hz, swara.cents_from_sa)
        annotated.append(frame.model_copy(update=updates))
    return annotated


def detect_sa_and_annotate(frames: list[PitchFrame]) -> tuple[list[PitchFrame], SaDetectionResult]:
    """Detect Sa, then enrich frames with cents and swara metadata."""
    result = detect_sa(frames)
    annotated = annotate_pitch_frames(frames, result.sa_hz)
    return annotated, result
