"""Single-page main window (Phase 7)."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QWidget


class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hindustani Classical Singing Analysis")
        self.setCentralWidget(QWidget(self))
