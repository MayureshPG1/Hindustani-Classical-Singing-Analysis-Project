"""Main window shell tests (pytest-qt)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from frontend.api_client import ApiError
from frontend.main_window import MainWindow
from frontend.widgets.summary_panel import EMPTY_TEXT, ComparisonSummaryPanel


class FakeApiClient:
    """In-memory API client for UI tests."""

    def __init__(self, *, fail_health: bool = False) -> None:
        self.fail_health = fail_health
        self.cleared = 0

    def health(self) -> dict[str, Any]:
        if self.fail_health:
            raise ApiError("backend_unavailable", "Backend down.", {})
        return {"status": "ok", "version": "0.1.0"}

    def inspect_audio(self, path: Path, *, role: str) -> dict[str, Any]:
        return {
            "file_info": {
                "file_id": f"{role}-1",
                "file_name": path.name,
                "duration_seconds": 1.2,
                "sample_rate": 44100,
                "channels": 1,
                "format": "wav",
                "validation_status": "valid",
                "error_message": None,
            },
            "pitch_metadata": {
                "voiced_frame_count": 40,
                "total_frame_count": 50,
                "voiced_fraction": 0.8,
            },
        }

    def compare_audio(
        self,
        guru_path: Path | None = None,
        disciple_path: Path | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return {
            "guru_file_info": {"file_name": "guru.wav"},
            "disciple_file_info": {"file_name": "disciple.wav"},
            "comparison_summary": {
                "overall_score": 90.0,
                "average_deviation_cents": 2.0,
                "match_percentage": 90.0,
                "higher_percentage": 5.0,
                "lower_percentage": 5.0,
                "tolerance_cents": 0,
            },
        }

    def get_comparison_pitch(self) -> dict[str, Any]:
        return {
            "guru_pitch_frames": [
                {"time_seconds": 0.0, "frequency_hz": 220.0, "voiced": True, "silent_or_unvoiced": False},
                {"time_seconds": 0.1, "frequency_hz": None, "voiced": False, "silent_or_unvoiced": True},
                {"time_seconds": 0.2, "frequency_hz": 230.0, "voiced": True, "silent_or_unvoiced": False},
            ],
            "disciple_pitch_frames": [
                {"time_seconds": 0.0, "frequency_hz": 225.0, "voiced": True, "silent_or_unvoiced": False},
                {"time_seconds": 0.2, "frequency_hz": 235.0, "voiced": True, "silent_or_unvoiced": False},
            ],
        }

    def clear_session(self) -> dict[str, Any]:
        self.cleared += 1
        return {"status": "cleared"}


def _open_window(qtbot, client: FakeApiClient | None = None) -> MainWindow:
    window = MainWindow(api_client=client or FakeApiClient(), check_health_on_open=False)
    window._on_health_ready({"status": "ok", "version": "0.1.0"})
    qtbot.addWidget(window)
    window.show()
    return window


def test_health_check_completes_async(qtbot) -> None:
    window = MainWindow(api_client=FakeApiClient(), check_health_on_open=True)
    qtbot.addWidget(window)
    window.show()
    qtbot.waitUntil(lambda: window._backend_ready, timeout=3000)
    assert "Ready" in window.status_bar.label.text()


def test_main_window_opens_and_has_upload_controls(qtbot) -> None:
    window = _open_window(qtbot)

    assert window.upload_panel.guru_button.isVisible()
    assert window.upload_panel.disciple_button.isVisible()
    assert window.upload_panel.compare_button.isVisible()
    assert window.upload_panel.clear_button.isVisible()


def test_compare_disabled_until_both_files_valid(qtbot, tmp_path: Path) -> None:
    window = _open_window(qtbot)

    assert not window.upload_panel.compare_button.isEnabled()

    guru = tmp_path / "guru.wav"
    disciple = tmp_path / "disciple.wav"
    guru.write_bytes(b"x")
    disciple.write_bytes(b"y")

    window._guru_path = guru
    window._disciple_path = disciple
    window._guru_valid = True
    window._disciple_valid = True
    window._refresh_compare_button()
    assert window.upload_panel.compare_button.isEnabled()


def test_summary_panel_formats_comparison_metrics() -> None:
    panel = ComparisonSummaryPanel()
    panel.show_summary(
        {
            "overall_score": 72.5,
            "average_deviation_cents": 18.3,
            "match_percentage": 72.5,
            "higher_percentage": 15.0,
            "lower_percentage": 12.5,
            "tolerance_cents": 10,
        }
    )
    assert panel._value_labels["overall_score"].text() == "72.5%"
    assert panel._value_labels["average_deviation_cents"].text() == "18.3 cents"
    assert panel._value_labels["tolerance_cents"].text() == "10 cents"
    panel.reset()
    assert panel._value_labels["overall_score"].text() == "—"
    assert EMPTY_TEXT in panel._placeholder.text()


def test_compare_populates_summary_panel(qtbot) -> None:
    window = _open_window(qtbot)
    window._on_compare_ready(
        {
            "compare": {
                "comparison_summary": {
                    "overall_score": 90.0,
                    "average_deviation_cents": 2.0,
                    "match_percentage": 90.0,
                    "higher_percentage": 5.0,
                    "lower_percentage": 5.0,
                    "tolerance_cents": 0,
                }
            },
            "pitch": {
                "guru_pitch_frames": [
                    {"time_seconds": 0.0, "frequency_hz": 220.0},
                ],
                "disciple_pitch_frames": [
                    {"time_seconds": 0.0, "frequency_hz": 225.0},
                ],
            },
        }
    )
    assert window.summary_panel._value_labels["overall_score"].text() == "90.0%"
    assert window.summary_panel._stack.currentIndex() == 1
    assert window.graph._stack.currentWidget() is window.graph._plot_widget


def test_compare_plots_graph_contours(qtbot) -> None:
    window = _open_window(qtbot)
    window._on_compare_ready(
        {
            "compare": {
                "comparison_summary": {
                    "overall_score": 90.0,
                    "average_deviation_cents": 2.0,
                    "match_percentage": 90.0,
                    "higher_percentage": 5.0,
                    "lower_percentage": 5.0,
                    "tolerance_cents": 0,
                }
            },
            "pitch": FakeApiClient().get_comparison_pitch(),
        }
    )
    guru_x, guru_y = window.graph._guru_curve.getData()
    assert guru_x is not None and len(guru_x) == 3
    assert guru_y is not None and len(guru_y) == 3


def test_error_popup_then_ui_reset(qtbot, monkeypatch) -> None:
    shown: list[str] = []

    def fake_critical(_parent, _title, message: str) -> int:
        shown.append(message)
        return int(QMessageBox.StandardButton.Ok)

    monkeypatch.setattr(QMessageBox, "critical", fake_critical)

    client = FakeApiClient()
    window = _open_window(qtbot, client)

    window._guru_path = Path("guru.wav")
    window._disciple_path = Path("disciple.wav")
    window._guru_valid = True
    window._disciple_valid = True
    window._show_error_and_reset(ApiError("no_vocals_detected", "No vocals detected.", {}))

    assert shown == ["No vocals detected."]
    assert client.cleared == 1
    assert window._guru_path is None
    assert window._disciple_path is None
    assert not window.upload_panel.compare_button.isEnabled()
    assert EMPTY_TEXT in window.summary_panel._placeholder.text()
