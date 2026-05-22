"""Processing status display."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StatusBar(QWidget):
    """Non-error processing status for the main workflow."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.label = QLabel("Status: Idle")
        self.label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

    def set_status(self, text: str) -> None:
        self.label.setText(f"Status: {text}")

    def reset(self) -> None:
        self.set_status("Idle")
