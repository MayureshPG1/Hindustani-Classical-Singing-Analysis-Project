"""Dual F0 contour graph (Hz vs wall-clock time)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QStackedWidget, QVBoxLayout, QWidget

from frontend.theme import COLOR_BG, COLOR_TEXT, COLOR_TEXT_MUTED, MUTED_LABEL_STYLE
from shared.constants import (
    PITCH_GRAPH_Y_MAX_HZ,
    PITCH_GRAPH_Y_MIN_HZ,
    SWARA_Y_AXIS_TICKS,
)

EMPTY_STATE_TEXT = "Upload guru and disciple audio to compare."

# UX: guru = darker reference line; disciple = contrasting overlay on black background.
DISCIPLE_LINE_WIDTH = 2
GURU_LINE_WIDTH = DISCIPLE_LINE_WIDTH * 3
GURU_PEN = pg.mkPen("#5a5a5a", width=GURU_LINE_WIDTH)
DISCIPLE_PEN = pg.mkPen("#5b9bd5", width=DISCIPLE_LINE_WIDTH)

SWARA_LABEL_FONT = QFont()
SWARA_LABEL_FONT.setPointSize(7)


def _configure_pitch_y_axis(plot_widget: pg.PlotWidget) -> None:
    """Fixed linear Hz range; auto ticks drive evenly spaced grid lines."""
    plot_widget.setLogMode(x=False, y=False)
    plot_widget.setYRange(PITCH_GRAPH_Y_MIN_HZ, PITCH_GRAPH_Y_MAX_HZ, padding=0)
    plot_widget.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)

    y_span = PITCH_GRAPH_Y_MAX_HZ - PITCH_GRAPH_Y_MIN_HZ
    view_box = plot_widget.getViewBox()
    view_box.setLimits(
        yMin=PITCH_GRAPH_Y_MIN_HZ,
        yMax=PITCH_GRAPH_Y_MAX_HZ,
        minYRange=y_span,
        maxYRange=y_span,
    )

    left_axis = plot_widget.getAxis("left")
    # Auto linear Hz ticks for grid; swara names are overlaid separately.
    left_axis.setTicks(None)
    left_axis.setStyle(showValues=False)


def _add_swara_axis_labels(plot_widget: pg.PlotWidget) -> list[pg.TextItem]:
    """Place swara names at true Hz on a linear Y axis (data coordinates)."""
    labels: list[pg.TextItem] = []
    for hz, name in SWARA_Y_AXIS_TICKS:
        item = pg.TextItem(name, color=COLOR_TEXT_MUTED, anchor=(1.0, 0.5))
        item.setFont(SWARA_LABEL_FONT)
        item.setPos(0.0, hz)
        item.setZValue(-5)
        plot_widget.addItem(item)
        labels.append(item)
    return labels


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

        _configure_pitch_y_axis(self._plot_widget)
        self._swara_labels = _add_swara_axis_labels(self._plot_widget)

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

        self._plot_widget.setLogMode(x=False, y=False)
        self._plot_widget.setYRange(
            PITCH_GRAPH_Y_MIN_HZ,
            PITCH_GRAPH_Y_MAX_HZ,
            padding=0,
        )

        self._stack.setCurrentWidget(self._plot_widget)

    def reset(self) -> None:
        self._guru_curve.setData([], [])
        self._disciple_curve.setData([], [])
        self.show_empty_state()
