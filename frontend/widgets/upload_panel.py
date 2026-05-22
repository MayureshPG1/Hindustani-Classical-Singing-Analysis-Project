"""Guru and disciple upload controls."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

FILE_FILTER = "Audio Files (*.wav *.mp3 *.m4a);;All Files (*)"


class UploadPanel(QWidget):
    """Upload buttons, per-file status, compare, and clear."""

    guru_upload_requested = Signal()
    disciple_upload_requested = Signal()
    compare_requested = Signal()
    clear_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        guru_row = QHBoxLayout()
        self.guru_button = QPushButton("Upload Guru Voice")
        self.guru_button.clicked.connect(self.guru_upload_requested.emit)
        self.guru_status = QLabel("Guru: no file selected")
        self.guru_status.setWordWrap(True)
        guru_row.addWidget(self.guru_button)
        guru_row.addWidget(self.guru_status, stretch=1)
        layout.addLayout(guru_row)

        disciple_row = QHBoxLayout()
        self.disciple_button = QPushButton("Upload Disciple Voice")
        self.disciple_button.clicked.connect(self.disciple_upload_requested.emit)
        self.disciple_status = QLabel("Disciple: no file selected")
        self.disciple_status.setWordWrap(True)
        disciple_row.addWidget(self.disciple_button)
        disciple_row.addWidget(self.disciple_status, stretch=1)
        layout.addLayout(disciple_row)

        action_row = QHBoxLayout()
        self.compare_button = QPushButton("Compare")
        self.compare_button.setEnabled(False)
        self.compare_button.setMinimumWidth(110)
        self.compare_button.setMinimumHeight(32)
        self.compare_button.clicked.connect(self.compare_requested.emit)
        self.clear_button = QPushButton("Clear")
        self.clear_button.setMinimumWidth(96)
        self.clear_button.setMinimumHeight(32)
        self.clear_button.clicked.connect(self.clear_requested.emit)
        action_row.addWidget(self.compare_button)
        action_row.addWidget(self.clear_button)
        action_row.addStretch()
        layout.addLayout(action_row)

        self.set_guru_status(empty=True)
        self.set_disciple_status(empty=True)

    def set_guru_status(
        self,
        *,
        empty: bool = False,
        loading: bool = False,
        file_name: str | None = None,
        duration_seconds: float | None = None,
        file_format: str | None = None,
        valid: bool = False,
        invalid_message: str | None = None,
    ) -> None:
        self.guru_status.setText(
            _format_status(
                role="Guru",
                empty=empty,
                loading=loading,
                file_name=file_name,
                duration_seconds=duration_seconds,
                file_format=file_format,
                valid=valid,
                invalid_message=invalid_message,
            )
        )

    def set_disciple_status(
        self,
        *,
        empty: bool = False,
        loading: bool = False,
        file_name: str | None = None,
        duration_seconds: float | None = None,
        file_format: str | None = None,
        valid: bool = False,
        invalid_message: str | None = None,
    ) -> None:
        self.disciple_status.setText(
            _format_status(
                role="Disciple",
                empty=empty,
                loading=loading,
                file_name=file_name,
                duration_seconds=duration_seconds,
                file_format=file_format,
                valid=valid,
                invalid_message=invalid_message,
            )
        )

    def set_compare_enabled(self, enabled: bool) -> None:
        self.compare_button.setEnabled(enabled)

    def set_controls_enabled(self, enabled: bool) -> None:
        self.guru_button.setEnabled(enabled)
        self.disciple_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        if not enabled:
            self.compare_button.setEnabled(False)

    def reset(self) -> None:
        self.set_guru_status(empty=True)
        self.set_disciple_status(empty=True)
        self.set_compare_enabled(False)
        self.set_controls_enabled(True)


def _format_status(
    *,
    role: str,
    empty: bool,
    loading: bool,
    file_name: str | None,
    duration_seconds: float | None,
    file_format: str | None,
    valid: bool,
    invalid_message: str | None,
) -> str:
    if empty:
        return f"{role}: no file selected"
    if loading:
        return f"{role}: loading and validating..."
    if file_name:
        duration_text = (
            f"{duration_seconds:.1f} s"
            if duration_seconds is not None
            else "duration unknown"
        )
        format_text = file_format or "unknown"
        state = "Valid" if valid else "Invalid"
        base = f"{role}: {file_name} — {duration_text} — {format_text} — {state}"
        if invalid_message and not valid:
            return f"{base} ({invalid_message})"
        return base
    return f"{role}: ready"
