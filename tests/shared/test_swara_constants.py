"""Tests for swara reference frequencies and graph Y-axis range."""

from __future__ import annotations

from shared.constants import (
    PITCH_GRAPH_Y_MAX_HZ,
    PITCH_GRAPH_Y_MIN_HZ,
    SWARA_FREQUENCIES_HZ,
    SWARA_Y_AXIS_TICKS,
)


def test_swara_frequencies_count_and_range() -> None:
    assert len(SWARA_FREQUENCIES_HZ) == 36
    freqs = list(SWARA_FREQUENCIES_HZ.values())
    assert min(freqs) == 125
    assert max(freqs) == 1000
    assert min(freqs) >= PITCH_GRAPH_Y_MIN_HZ
    assert max(freqs) <= PITCH_GRAPH_Y_MAX_HZ


def test_swara_y_axis_ticks_sorted_by_frequency() -> None:
    assert len(SWARA_Y_AXIS_TICKS) == 36
    hz_values = [hz for hz, _ in SWARA_Y_AXIS_TICKS]
    assert hz_values == sorted(hz_values)
    for hz, name in SWARA_Y_AXIS_TICKS:
        assert SWARA_FREQUENCIES_HZ[name] == hz
