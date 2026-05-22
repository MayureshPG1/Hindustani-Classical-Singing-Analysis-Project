"""Single-page main window."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QObject, QThread, Signal, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from frontend.api_client import ApiError, HcsaApiClient
from frontend.theme import SUBTITLE_STYLE, TITLE_STYLE
from frontend.validation import validate_upload_path
from frontend.widgets.bordered_cluster import create_bordered_cluster
from frontend.widgets.comparison_graph import ComparisonGraph
from frontend.widgets.status_bar import StatusBar
from frontend.widgets.summary_panel import ComparisonSummaryPanel
from frontend.widgets.upload_panel import FILE_FILTER, UploadPanel

APP_TITLE = "Hindustani Classical Singing Analysis"
APP_SUBTITLE = "Guru vs Disciple Pitch Comparison"


class _ApiThread(QThread):
    """Run a blocking API call off the UI thread."""

    succeeded = Signal(object)
    failed = Signal(object)

    def __init__(
        self,
        fn: Callable[[], Any],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._fn = fn

    def run(self) -> None:
        try:
            self.succeeded.emit(self._fn())
        except ApiError as exc:
            self.failed.emit(exc)
        except Exception as exc:
            self.failed.emit(
                ApiError("comparison_failed", str(exc) or "Unexpected error.", {})
            )


class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(
        self,
        api_client: HcsaApiClient | None = None,
        *,
        check_health_on_open: bool = True,
    ) -> None:
        super().__init__()
        self._client = api_client or HcsaApiClient()
        self._guru_path: Path | None = None
        self._disciple_path: Path | None = None
        self._guru_valid = False
        self._disciple_valid = False
        self._busy = False
        self._backend_ready = False
        self._active_thread: _ApiThread | None = None
        self._build_ui()
        self._wire_signals()
        if check_health_on_open:
            self._check_backend_health()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._active_thread is not None and self._active_thread.isRunning():
            self._active_thread.requestInterruption()
            self._active_thread.quit()
            self._active_thread.wait(3000)
        super().closeEvent(event)

    def _build_ui(self) -> None:
        self.setWindowTitle(APP_TITLE)
        self.resize(960, 720)

        central = QWidget(self)
        layout = QVBoxLayout(central)

        title = QLabel(APP_TITLE)
        title.setStyleSheet(TITLE_STYLE)
        subtitle = QLabel(APP_SUBTITLE)
        subtitle.setStyleSheet(SUBTITLE_STYLE)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.graph = ComparisonGraph(central)
        layout.addWidget(self.graph, stretch=1)

        control_row = QWidget(central)
        control_layout = QHBoxLayout(control_row)
        control_layout.setContentsMargins(0, 8, 0, 8)
        control_layout.setSpacing(12)

        self.upload_panel = UploadPanel(control_row)
        self.summary_panel = ComparisonSummaryPanel(control_row)

        uploads_cluster = create_bordered_cluster(self.upload_panel, parent=control_row)
        metrics_cluster = create_bordered_cluster(
            self.summary_panel,
            parent=control_row,
            margins=(10, 10, 10, 10),
        )

        control_layout.addWidget(uploads_cluster, stretch=1)
        control_layout.addWidget(
            metrics_cluster,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )
        layout.addWidget(control_row)

        self.status_bar = StatusBar(central)
        layout.addWidget(self.status_bar)

        self.setCentralWidget(central)

    def _wire_signals(self) -> None:
        panel = self.upload_panel
        panel.guru_upload_requested.connect(self._on_upload_guru)
        panel.disciple_upload_requested.connect(self._on_upload_disciple)
        panel.compare_requested.connect(self._on_compare)
        panel.clear_requested.connect(self._on_clear)

    def _check_backend_health(self) -> None:
        self.status_bar.set_status("Checking backend...")
        self._run_api_task(self._client.health, self._on_health_ready, block_ui=False)

    def _on_health_ready(self, payload: object) -> None:
        if isinstance(payload, dict) and payload.get("status") == "ok":
            self._backend_ready = True
            self.status_bar.set_status("Ready — upload guru and disciple audio.")
            return
        self._backend_ready = False
        self._show_error_popup(
            ApiError(
                "backend_unavailable",
                "The analysis server did not respond correctly.",
                {},
            )
        )
        self._reset_ui_state()

    def _on_upload_guru(self) -> None:
        self._pick_and_inspect(role="guru")

    def _on_upload_disciple(self) -> None:
        self._pick_and_inspect(role="disciple")

    def _pick_and_inspect(self, *, role: str) -> None:
        if self._busy or not self._backend_ready:
            return
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {role.title()} Audio",
            "",
            FILE_FILTER,
        )
        if not path_str:
            return

        path = Path(path_str)
        client_error = validate_upload_path(path)
        if client_error:
            self._show_error_popup(ApiError("unsupported_file_type", client_error, {}))
            self._clear_session_and_reset()
            return

        if role == "guru":
            self._guru_path = path
            self._guru_valid = False
            self.upload_panel.set_guru_status(loading=True)
        else:
            self._disciple_path = path
            self._disciple_valid = False
            self.upload_panel.set_disciple_status(loading=True)

        self._refresh_compare_button()
        self.status_bar.set_status(f"Validating {role} audio...")
        self._run_api_task(
            lambda: self._client.inspect_audio(path, role=role),
            lambda payload, r=role: self._on_inspect_ready(r, payload),
        )

    def _on_inspect_ready(self, role: str, payload: object) -> None:
        if not isinstance(payload, dict):
            self._show_error_popup(
                ApiError("comparison_failed", "Invalid inspect response.", {})
            )
            self._clear_session_and_reset()
            return

        file_info = payload.get("file_info", {})
        if not isinstance(file_info, dict):
            self._show_error_popup(
                ApiError("comparison_failed", "Invalid inspect response.", {})
            )
            self._clear_session_and_reset()
            return

        file_name = str(file_info.get("file_name", ""))
        duration = file_info.get("duration_seconds")
        file_format = str(file_info.get("format", "unknown"))
        valid = file_info.get("validation_status") == "valid"

        if role == "guru":
            self._guru_valid = valid
            self.upload_panel.set_guru_status(
                file_name=file_name,
                duration_seconds=float(duration) if duration is not None else None,
                file_format=file_format,
                valid=valid,
            )
        else:
            self._disciple_valid = valid
            self.upload_panel.set_disciple_status(
                file_name=file_name,
                duration_seconds=float(duration) if duration is not None else None,
                file_format=file_format,
                valid=valid,
            )

        self._refresh_compare_button()
        if valid:
            self.status_bar.set_status(f"{role.title()} file validated.")
            return

        message = str(file_info.get("error_message") or "File validation failed.")
        self._show_error_popup(ApiError("comparison_failed", message, {}))
        self._clear_session_and_reset()

    def _on_compare(self) -> None:
        if self._busy or not self._can_compare():
            return
        assert self._guru_path is not None
        assert self._disciple_path is not None

        self.status_bar.set_status("Comparing recordings...")
        self.graph.show_empty_state()
        self.summary_panel.show_empty()
        self._run_api_task(
            lambda: self._client.compare_audio(),
            self._on_compare_ready,
        )

    def _on_compare_ready(self, payload: object) -> None:
        if not isinstance(payload, dict) or "comparison_summary" not in payload:
            self._show_error_popup(
                ApiError("comparison_failed", "Invalid compare response.", {})
            )
            self._clear_session_and_reset()
            return

        summary = payload.get("comparison_summary")
        if isinstance(summary, dict):
            self.summary_panel.show_summary(summary)
        else:
            self.summary_panel.show_empty()
        self.status_bar.set_status("Comparison complete.")
        self.graph.show_empty_state()

    def _on_clear(self) -> None:
        if self._busy:
            return
        self._run_api_task(self._client.clear_session, self._on_clear_complete, block_ui=False)

    def _on_clear_complete(self, _payload: object) -> None:
        self._reset_ui_state()

    def _show_error_popup(self, error: ApiError) -> None:
        QMessageBox.critical(self, "Error", error.message)

    def _show_error_and_reset(self, error: ApiError) -> None:
        self._show_error_popup(error)
        self._clear_session_and_reset()

    def _clear_session_and_reset(self) -> None:
        try:
            self._client.clear_session()
        except ApiError:
            pass
        self._reset_ui_state()

    def _reset_ui_state(self) -> None:
        self._guru_path = None
        self._disciple_path = None
        self._guru_valid = False
        self._disciple_valid = False
        self.upload_panel.reset()
        self.summary_panel.reset()
        self.graph.reset()
        if self._backend_ready:
            self.status_bar.set_status("Ready — upload guru and disciple audio.")
        else:
            self.status_bar.reset()
        self._refresh_compare_button()

    def _can_compare(self) -> bool:
        return (
            self._backend_ready
            and self._guru_valid
            and self._disciple_valid
            and self._guru_path is not None
            and self._disciple_path is not None
        )

    def _refresh_compare_button(self) -> None:
        self.upload_panel.set_compare_enabled(self._can_compare() and not self._busy)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.upload_panel.set_controls_enabled(not busy)
        self._refresh_compare_button()

    def _run_api_task(
        self,
        fn: Callable[[], Any],
        on_success: Callable[[object], None],
        *,
        block_ui: bool = True,
    ) -> None:
        if self._active_thread is not None and self._active_thread.isRunning():
            return

        thread = _ApiThread(fn, parent=self)
        if block_ui:
            self._set_busy(True)

        thread.succeeded.connect(on_success, Qt.ConnectionType.QueuedConnection)
        thread.failed.connect(self._show_error_and_reset, Qt.ConnectionType.QueuedConnection)
        thread.finished.connect(
            lambda: self._on_api_thread_finished(block_ui),
            Qt.ConnectionType.QueuedConnection,
        )

        self._active_thread = thread
        thread.start()

    def _on_api_thread_finished(self, block_ui: bool) -> None:
        if block_ui:
            self._set_busy(False)
        sender = self.sender()
        if isinstance(sender, _ApiThread) and self._active_thread is sender:
            self._active_thread = None
