"""Phase 1 API tests: health, tolerance, clear session."""

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


def test_get_tolerance_defaults(client: TestClient) -> None:
    response = client.get("/api/v1/settings/tolerance")
    assert response.status_code == 200
    data = response.json()
    assert data["tolerance_cents"] == 0
    assert data["default_tolerance_cents"] == 0
    assert data["step_cents"] == 5
    assert data["minimum_tolerance_cents"] == 0
    assert data["maximum_tolerance_cents"] == 25


def test_put_tolerance_updates_value(client: TestClient) -> None:
    response = client.put("/api/v1/settings/tolerance", json={"tolerance_cents": 15})
    assert response.status_code == 200
    assert response.json()["tolerance_cents"] == 15

    get_response = client.get("/api/v1/settings/tolerance")
    assert get_response.json()["tolerance_cents"] == 15


@pytest.mark.parametrize("bad_value", [-1, 26, 100])
def test_put_tolerance_rejects_out_of_range(client: TestClient, bad_value: float) -> None:
    response = client.put("/api/v1/settings/tolerance", json={"tolerance_cents": bad_value})
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "invalid_tolerance"
    assert "tolerance" in data["message"].lower()


def test_put_tolerance_rejects_non_numeric(client: TestClient) -> None:
    response = client.put("/api/v1/settings/tolerance", json={"tolerance_cents": "abc"})
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "invalid_tolerance"


def test_clear_session_returns_cleared(client: TestClient) -> None:
    client.put("/api/v1/settings/tolerance", json={"tolerance_cents": 20})
    response = client.post("/api/v1/session/clear")
    assert response.status_code == 200
    assert response.json() == {"status": "cleared"}

    tolerance = client.get("/api/v1/settings/tolerance").json()
    assert tolerance["tolerance_cents"] == 0


def test_clear_session_deletes_temp_files(client: TestClient) -> None:
    app = client.app
    session: SessionManager = app.state.session_manager
    temp_file = session.temp_root / "guru-test.wav"
    temp_file.write_bytes(b"RIFF")
    assert temp_file.exists()

    client.post("/api/v1/session/clear")
    assert not temp_file.exists()
    assert session.temp_root.exists()


def test_swara_map_returns_twelve_items(client: TestClient) -> None:
    response = client.get("/api/v1/swara-map")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 12
    assert items[0]["symbol"] == "S"
    assert items[-1]["symbol"] == "N"


def test_hcsa_error_response_shape() -> None:
    from backend.app.models.errors import ErrorResponse

    body = ErrorResponse(
        error_code="invalid_tolerance",
        message="Tolerance must be numeric and within the allowed range.",
        details={"tolerance_cents": 99},
    )
    dumped = body.model_dump()
    assert dumped["error_code"] == "invalid_tolerance"
    assert dumped["details"]["tolerance_cents"] == 99
