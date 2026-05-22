"""Dual F0 contour graph (Hz vs wall-clock time)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QStackedWidget, QVBoxLayout, QWidget

from frontend.theme import (
    CLUSTER_FRAME_STYLE,
    COLOR_BG,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    MUTED_LABEL_STYLE,
)
from shared.constants import (
    PITCH_GRAPH_Y_MAX_HZ,
    PITCH_GRAPH_Y_MIN_HZ,
    SWARA_Y_AXIS_TICKS,
)

EMPTY_STATE_TEXT = "Upload guru and disciple audio to compare."

# Default X span before comparison (wall-clock seconds); axis never goes below 0.
PITCH_GRAPH_DEFAULT_X_MAX_S = 30.0

# UX: guru = darker reference line; disciple = contrasting overlay on black background.
DISCIPLE_LINE_WIDTH = 2
GURU_LINE_WIDTH = DISCIPLE_LINE_WIDTH * 4
GURU_PEN = pg.mkPen("#5a4a20", width=GURU_LINE_WIDTH)
DISCIPLE_PEN = pg.mkPen("#F4C430", width=DISCIPLE_LINE_WIDTH)

Y_AXIS_VIEW_PADDING = 0.04
LEFT_AXIS_WIDTH = 56


def _swara_y_ticks() -> list[tuple[float, str]]:
    return [(hz, name) for hz, name in SWARA_Y_AXIS_TICKS]


def _configure_pitch_x_axis(plot_widget: pg.PlotWidget) -> None:
    """Wall-clock X from 0 s; no negative ticks (padding=0 on lower bound)."""
    plot_widget.enableAutoRange(axis=pg.ViewBox.XAxis, enable=False)
    plot_widget.setXRange(0.0, PITCH_GRAPH_DEFAULT_X_MAX_S, padding=0)

    view_box = plot_widget.getViewBox()
    view_box.setLimits(xMin=0.0, minXRange=0.1)


def _configure_pitch_y_axis(plot_widget: pg.PlotWidget) -> None:
    """Fixed linear Hz range with swara names on the left axis."""
    plot_widget.setLogMode(x=False, y=False)
    plot_widget.setYRange(
        PITCH_GRAPH_Y_MIN_HZ,
        PITCH_GRAPH_Y_MAX_HZ,
        padding=Y_AXIS_VIEW_PADDING,
    )
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
    left_axis.setWidth(LEFT_AXIS_WIDTH)
    left_axis.setTicks([_swara_y_ticks()])
    left_axis.setStyle(showValues=True)
    left_axis.setPen(pg.mkPen(COLOR_TEXT_MUTED))
    left_axis.setTextPen(pg.mkPen(COLOR_TEXT))

    plot_item = plot_widget.getPlotItem()
    plot_item.layout.setContentsMargins(4, 10, 4, 4)


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
        self._stack = QStackedWidget()

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
        bottom_axis = self._plot_widget.getAxis("bottom")
        bottom_axis.setPen(pg.mkPen(COLOR_TEXT_MUTED))
        bottom_axis.setTextPen(pg.mkPen(COLOR_TEXT))

        _configure_pitch_x_axis(self._plot_widget)
        _configure_pitch_y_axis(self._plot_widget)

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

        graph_frame = QFrame(self)
        graph_frame.setObjectName("GraphCluster")
        graph_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        graph_frame.setStyleSheet(CLUSTER_FRAME_STYLE)

        frame_layout = QVBoxLayout(graph_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(0)
        frame_layout.addWidget(self._stack)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(graph_frame)
        self.setMinimumHeight(240)

        self.show_empty_state()

    def show_empty_state(self) -> None:
        self.placeholder.setText(EMPTY_STATE_TEXT)
        self._stack.setCurrentWidget(self.placeholder)
        _configure_pitch_x_axis(self._plot_widget)

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
        x_max = max(max_time * 1.02, 0.1)
        self._plot_widget.setXRange(0.0, x_max, padding=0)

        self._plot_widget.setLogMode(x=False, y=False)
        self._plot_widget.setYRange(
            PITCH_GRAPH_Y_MIN_HZ,
            PITCH_GRAPH_Y_MAX_HZ,
            padding=Y_AXIS_VIEW_PADDING,
        )
        _configure_pitch_y_axis(self._plot_widget)

        self._stack.setCurrentWidget(self._plot_widget)

    def reset(self) -> None:
        self._guru_curve.setData([], [])
        self._disciple_curve.setData([], [])
        self.show_empty_state()
