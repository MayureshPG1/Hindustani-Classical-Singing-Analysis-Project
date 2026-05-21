"""API tests: health, clear session."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.core.session import SessionManager
from backend.app.main import create_app


@pytest.fixture
def client() -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok", "version": "0.1.0"}


def test_clear_session_returns_cleared(client: TestClient) -> None:
    response = client.post("/api/v1/session/clear")
    assert response.status_code == 200
    assert response.json() == {"status": "cleared"}


def test_clear_session_deletes_temp_files(client: TestClient) -> None:
    app = client.app
    session: SessionManager = app.state.session_manager
    temp_file = session.temp_root / "guru-test.wav"
    temp_file.write_bytes(b"RIFF")
    assert temp_file.exists()

    client.post("/api/v1/session/clear")
    assert not temp_file.exists()
    assert session.temp_root.exists()


def test_tolerance_endpoint_removed(client: TestClient) -> None:
    assert client.get("/api/v1/settings/tolerance").status_code == 404
    assert client.put("/api/v1/settings/tolerance", json={"tolerance_cents": 0}).status_code == 404


def test_swara_map_endpoint_removed(client: TestClient) -> None:
    assert client.get("/api/v1/swara-map").status_code == 404


def test_hcsa_error_response_shape() -> None:
    from backend.app.models.errors import ErrorResponse

    body = ErrorResponse(
        error_code="no_vocals_detected",
        message="No reliable vocal pitch was detected.",
        details={"role": "guru"},
    )
    dumped = body.model_dump()
    assert dumped["error_code"] == "no_vocals_detected"
    assert dumped["details"]["role"] == "guru"
