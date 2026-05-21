"""Phase 0: verify package layout and imports."""

from __future__ import annotations

import importlib
import sys

import pytest

BACKEND_MODULES = [
    "backend.app.main",
    "backend.app.core.config",
    "backend.app.core.errors",
    "backend.app.api.routes_health",
    "backend.app.api.routes_audio",
    "backend.app.api.routes_compare",
    "backend.app.models.audio",
    "backend.app.models.comparison",
    "backend.app.models.errors",
    "backend.app.models.swara",
    "backend.app.services.audio_loader",
    "backend.app.services.pitch_extractor",
    "backend.app.services.sa_detector",
    "backend.app.services.swara_mapper",
    "backend.app.services.matched_portion_finder",
    "backend.app.services.aligner",
    "backend.app.services.scorer",
    "backend.app.services.comparator",
]

FRONTEND_MODULES = [
    "frontend.main_window",
    "frontend.api_client",
    "frontend.backend_manager",
    "frontend.validation",
    "frontend.widgets.upload_panel",
    "frontend.widgets.tolerance_control",
    "frontend.widgets.comparison_graph",
    "frontend.widgets.summary_panel",
    "frontend.widgets.status_bar",
]


@pytest.mark.parametrize("module_name", BACKEND_MODULES)
def test_backend_module_imports(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert module is not None


@pytest.mark.parametrize("module_name", FRONTEND_MODULES)
def test_frontend_module_imports(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert module is not None


def test_shared_constants() -> None:
    from shared.constants import (
        API_BASE_URL,
        DEFAULT_TOLERANCE_CENTS,
        MAX_TOLERANCE_CENTS,
        SWARA_TABLE,
    )

    assert API_BASE_URL == "http://127.0.0.1:8765/api/v1"
    assert DEFAULT_TOLERANCE_CENTS == 0.0
    assert MAX_TOLERANCE_CENTS == 25.0
    assert len(SWARA_TABLE) == 12


def test_backend_config_matches_architecture() -> None:
    from backend.app.core import config

    assert config.SR == 22050
    assert config.HOP_LENGTH == 220
    assert config.VOICED_PROB_PLOT_MIN == 0.55
    assert config.MIN_WINDOW_SECONDS == 1.0


def test_fastapi_app_factory() -> None:
    from backend.app.main import app, create_app

    assert app.title == "HCSA Backend"
    assert create_app().version == "0.1.0"


def test_frontend_validation_rejects_bad_extension(tmp_path) -> None:
    from frontend.validation import validate_upload_path

    bad = tmp_path / "track.m4a"
    bad.write_bytes(b"\x00\x01")
    assert validate_upload_path(bad) is not None
