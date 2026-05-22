"""Post-comparison metrics panel (third row, bottom-right)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QStackedWidget, QVBoxLayout, QWidget

from frontend.theme import COLOR_TEXT, MUTED_LABEL_STYLE, TRANSPARENT_WIDGET_STYLE

EMPTY_TEXT = "Comparison metrics appear here after Compare."

_METRIC_ROWS: tuple[tuple[str, str], ...] = (
    ("overall_score", "Match score"),
    ("average_deviation_cents", "Avg deviation"),
    ("match_percentage", "Match"),
    ("higher_percentage", "Higher"),
    ("lower_percentage", "Lower"),
    ("tolerance_cents", "Tolerance"),
)

# Fixed size so showing metrics does not resize the control row.
_PANEL_MIN_HEIGHT = 188
_PANEL_WIDTH = 248


class ComparisonSummaryPanel(QWidget):
    """Displays ``comparison_summary`` from POST /compare."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value_labels: dict[str, QLabel] = {}
        self.setFixedWidth(_PANEL_WIDTH)
        self.setMinimumHeight(_PANEL_MIN_HEIGHT)
        self._build_ui()
        self.show_empty()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        self.title = QLabel("Comparison")
        self.title.setStyleSheet(
            f"font-weight: bold; background: transparent; color: {COLOR_TEXT};"
        )
        outer.addWidget(self.title)

        self._stack = QStackedWidget(self)
        self._stack.setFixedHeight(_PANEL_MIN_HEIGHT - 28)
        self._stack.setStyleSheet(TRANSPARENT_WIDGET_STYLE)

        placeholder_page = QWidget()
        placeholder_page.setStyleSheet(TRANSPARENT_WIDGET_STYLE)
        placeholder_layout = QVBoxLayout(placeholder_page)
        placeholder_layout.setContentsMargins(4, 4, 4, 4)
        self._placeholder = QLabel(EMPTY_TEXT)
        self._placeholder.setWordWrap(True)
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet(f"{MUTED_LABEL_STYLE} font-size: 11px;")
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(self._placeholder)
        placeholder_layout.addStretch()
        self._stack.addWidget(placeholder_page)

        metrics_page = QWidget()
        metrics_page.setStyleSheet(TRANSPARENT_WIDGET_STYLE)
        grid = QGridLayout(metrics_page)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(4)

        for row, (key, label_text) in enumerate(_METRIC_ROWS):
            name_label = QLabel(f"{label_text}:")
            name_label.setStyleSheet(TRANSPARENT_WIDGET_STYLE)
            name_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            value_label = QLabel("—")
            value_label.setStyleSheet(TRANSPARENT_WIDGET_STYLE)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            value_label.setMinimumWidth(76)
            grid.addWidget(name_label, row, 0)
            grid.addWidget(value_label, row, 1)
            self._value_labels[key] = value_label

        self._stack.addWidget(metrics_page)
        outer.addWidget(self._stack)

    def show_empty(self) -> None:
        self._stack.setCurrentIndex(0)
        self._placeholder.setText(EMPTY_TEXT)
        for label in self._value_labels.values():
            label.setText("—")

    def show_summary(self, summary: dict[str, Any]) -> None:
        overall = float(summary.get("overall_score", 0.0))
        avg_cents = float(summary.get("average_deviation_cents", 0.0))
        match_pct = float(summary.get("match_percentage", 0.0))
        higher_pct = float(summary.get("higher_percentage", 0.0))
        lower_pct = float(summary.get("lower_percentage", 0.0))
        tolerance = int(summary.get("tolerance_cents", 0))

        self._value_labels["overall_score"].setText(f"{overall:.1f}%")
        self._value_labels["average_deviation_cents"].setText(f"{avg_cents:.1f} cents")
        self._value_labels["match_percentage"].setText(f"{match_pct:.1f}%")
        self._value_labels["higher_percentage"].setText(f"{higher_pct:.1f}%")
        self._value_labels["lower_percentage"].setText(f"{lower_pct:.1f}%")
        self._value_labels["tolerance_cents"].setText(f"{tolerance} cents")
        self._stack.setCurrentIndex(1)

    def reset(self) -> None:
        self.show_empty()
