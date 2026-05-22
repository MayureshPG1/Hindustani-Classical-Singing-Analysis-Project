"""Wall-clock Hz comparison and summary metrics (no Sa / DTW)."""

from __future__ import annotations

import math
from bisect import bisect_left

from backend.app.core.errors import raise_comparison_failed
from backend.app.models.comparison import ComparisonSummary
from backend.app.models.pitch import PitchFrame


def _is_scorable(frame: PitchFrame) -> bool:
    return frame.voiced and frame.frequency_hz is not None and frame.frequency_hz > 0.0


def deviation_cents(guru_hz: float, disciple_hz: float) -> float:
    """Instantaneous pitch difference in cents (Hz ratio, no Sa)."""
    return 1200.0 * math.log2(disciple_hz / guru_hz)


def _nearest_disciple_index(disciple_times: list[float], target_time: float) -> int:
    if not disciple_times:
        return 0
    pos = bisect_left(disciple_times, target_time)
    if pos <= 0:
        return 0
    if pos >= len(disciple_times):
        return len(disciple_times) - 1
    before = disciple_times[pos - 1]
    after = disciple_times[pos]
    return pos - 1 if (target_time - before) <= (after - target_time) else pos


def _classify(deviation: float, tolerance_cents: int) -> str:
    if abs(deviation) <= tolerance_cents:
        return "match"
    if deviation > tolerance_cents:
        return "higher"
    return "lower"


def score_wall_clock(
    guru_frames: list[PitchFrame],
    disciple_frames: list[PitchFrame],
    *,
    tolerance_cents: int,
    guru_duration_seconds: float,
    disciple_duration_seconds: float,
) -> ComparisonSummary:
    """
    Pair guru and disciple frames by nearest wall-clock time within overlap.

    Only scores frames where both sides are voiced with valid Hz.
    """
    overlap_end = min(guru_duration_seconds, disciple_duration_seconds)
    disciple_times = [f.time_seconds for f in disciple_frames]

    match_count = 0
    higher_count = 0
    lower_count = 0
    abs_deviations: list[float] = []

    for guru_frame in guru_frames:
        if guru_frame.time_seconds > overlap_end:
            break
        if not _is_scorable(guru_frame):
            continue

        idx = _nearest_disciple_index(disciple_times, guru_frame.time_seconds)
        disciple_frame = disciple_frames[idx]
        if disciple_frame.time_seconds > overlap_end or not _is_scorable(disciple_frame):
            continue

        guru_hz = guru_frame.frequency_hz
        disciple_hz = disciple_frame.frequency_hz
        assert guru_hz is not None and disciple_hz is not None

        dev = deviation_cents(guru_hz, disciple_hz)
        label = _classify(dev, tolerance_cents)
        abs_deviations.append(abs(dev))

        if label == "match":
            match_count += 1
        elif label == "higher":
            higher_count += 1
        else:
            lower_count += 1

    scored_count = match_count + higher_count + lower_count
    if scored_count == 0:
        raise_comparison_failed("no overlapping voiced frame pairs")

    def pct(count: int) -> float:
        return round(count * 100.0 / scored_count, 2)

    match_pct = pct(match_count)
    avg_dev = round(sum(abs_deviations) / len(abs_deviations), 2)

    return ComparisonSummary(
        overall_score=match_pct,
        average_deviation_cents=avg_dev,
        match_percentage=match_pct,
        higher_percentage=pct(higher_count),
        lower_percentage=pct(lower_count),
        tolerance_cents=tolerance_cents,
    )
