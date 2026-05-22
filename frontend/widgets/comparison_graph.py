"""Graph placeholder until Phase 6 pyqtgraph overlay."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from frontend.theme import MUTED_LABEL_STYLE

EMPTY_STATE_TEXT = "Upload guru and disciple audio to compare."


class ComparisonGraph(QWidget):
    """Placeholder graph region (dual F0 overlay added in Phase 6)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.placeholder = QLabel(EMPTY_STATE_TEXT)
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setWordWrap(True)
        self.placeholder.setStyleSheet(MUTED_LABEL_STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(self.placeholder)
        self.setMinimumHeight(240)

    def show_empty_state(self) -> None:
        self.placeholder.setText(EMPTY_STATE_TEXT)
        self.placeholder.show()

    def reset(self) -> None:
        self.show_empty_state()
