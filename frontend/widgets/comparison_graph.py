"""Dual F0 contour graph (Hz vs wall-clock time)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QStackedWidget, QVBoxLayout, QWidget

from frontend.theme import COLOR_BG, COLOR_TEXT, COLOR_TEXT_MUTED, MUTED_LABEL_STYLE

EMPTY_STATE_TEXT = "Upload guru and disciple audio to compare."

# UX: guru = darker reference line; disciple = contrasting overlay on black background.
GURU_PEN = pg.mkPen("#5a5a5a", width=2)
DISCIPLE_PEN = pg.mkPen("#5b9bd5", width=2)


def pitch_frames_to_plot_arrays(
    frames: Sequence[Mapping[str, Any]],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Map pitch frames to X (seconds) and Y (Hz) with NaN gaps for unvoiced frames.

    Plots only frames with a reliable frequency_hz; unvoiced segments break the line.
    """
    if not frames:
        return np.array([], dtype=np.float64), np.array([], dtype=np.float64)

    times: list[float] = []
    frequencies: list[float] = []
    for frame in frames:
        time_s = float(frame["time_seconds"])
        hz = frame.get("frequency_hz")
        times.append(time_s)
        if hz is not None and float(hz) > 0.0:
            frequencies.append(float(hz))
        else:
            frequencies.append(float("nan"))

    return np.asarray(times, dtype=np.float64), np.asarray(frequencies, dtype=np.float64)


class ComparisonGraph(QWidget):
    """pyqtgraph overlay of guru and disciple pitch contours."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._stack = QStackedWidget(self)

        self.placeholder = QLabel(EMPTY_STATE_TEXT)
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setWordWrap(True)
        self.placeholder.setStyleSheet(MUTED_LABEL_STYLE)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground(COLOR_BG)
        self._plot_widget.setLabel("bottom", "Time", units="s")
        self._plot_widget.setLabel("left", "Frequency", units="Hz")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.25)
        self._plot_widget.addLegend(offset=(10, 10))
        for axis_name in ("bottom", "left"):
            axis = self._plot_widget.getAxis(axis_name)
            axis.setPen(pg.mkPen(COLOR_TEXT_MUTED))
            axis.setTextPen(pg.mkPen(COLOR_TEXT))

        self._guru_curve = self._plot_widget.plot(
            pen=GURU_PEN,
            name="Guru",
            connect="finite",
        )
        self._disciple_curve = self._plot_widget.plot(
            pen=DISCIPLE_PEN,
            name="Disciple",
            connect="finite",
        )

        self._stack.addWidget(self.placeholder)
        self._stack.addWidget(self._plot_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack)
        self.setMinimumHeight(240)

        self.show_empty_state()

    def show_empty_state(self) -> None:
        self.placeholder.setText(EMPTY_STATE_TEXT)
        self._stack.setCurrentWidget(self.placeholder)

    def plot_contours(
        self,
        guru_frames: Sequence[Mapping[str, Any]],
        disciple_frames: Sequence[Mapping[str, Any]],
    ) -> None:
        """Render guru and disciple F0 contours with gaps for unvoiced frames."""
        guru_x, guru_y = pitch_frames_to_plot_arrays(guru_frames)
        disciple_x, disciple_y = pitch_frames_to_plot_arrays(disciple_frames)

        self._guru_curve.setData(guru_x, guru_y)
        self._disciple_curve.setData(disciple_x, disciple_y)

        max_time = 0.0
        if guru_x.size:
            max_time = max(max_time, float(np.nanmax(guru_x)))
        if disciple_x.size:
            max_time = max(max_time, float(np.nanmax(disciple_x)))
        if max_time > 0.0:
            self._plot_widget.setXRange(0.0, max_time * 1.02, padding=0.02)

        voiced_hz: list[float] = []
        for series in (guru_y, disciple_y):
            valid = series[~np.isnan(series)]
            if valid.size:
                voiced_hz.extend(valid.tolist())
        if voiced_hz:
            y_min = max(50.0, min(voiced_hz) * 0.9)
            y_max = min(1000.0, max(voiced_hz) * 1.1)
            if y_max > y_min:
                self._plot_widget.setYRange(y_min, y_max, padding=0.05)

        self._stack.setCurrentWidget(self._plot_widget)

    def reset(self) -> None:
        self._guru_curve.setData([], [])
        self._disciple_curve.setData([], [])
        self.show_empty_state()
