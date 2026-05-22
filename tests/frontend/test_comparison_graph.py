"""Unit tests for pitch contour plot data."""

from __future__ import annotations

import math

import numpy as np

from frontend.widgets.comparison_graph import (
    DISCIPLE_LINE_WIDTH,
    GURU_LINE_WIDTH,
    pitch_frames_to_plot_arrays,
)


def test_guru_line_is_four_times_disciple_width() -> None:
    assert GURU_LINE_WIDTH == DISCIPLE_LINE_WIDTH * 4


def test_pitch_frames_to_plot_arrays_inserts_nan_gaps() -> None:
    frames = [
        {"time_seconds": 0.0, "frequency_hz": 220.0},
        {"time_seconds": 0.1, "frequency_hz": None},
        {"time_seconds": 0.2, "frequency_hz": 230.0},
    ]
    times, freqs = pitch_frames_to_plot_arrays(frames)

    assert times.tolist() == [0.0, 0.1, 0.2]
    assert freqs[0] == 220.0
    assert math.isnan(freqs[1])
    assert freqs[2] == 230.0


def test_pitch_frames_to_plot_arrays_empty() -> None:
    times, freqs = pitch_frames_to_plot_arrays([])
    assert times.size == 0
    assert freqs.size == 0


def test_pitch_frames_to_plot_arrays_skips_non_positive_hz() -> None:
    frames = [
        {"time_seconds": 0.0, "frequency_hz": 0.0},
        {"time_seconds": 0.1, "frequency_hz": 200.0},
    ]
    _, freqs = pitch_frames_to_plot_arrays(frames)
    assert math.isnan(freqs[0])
    assert freqs[1] == 200.0
