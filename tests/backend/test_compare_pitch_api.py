"""GET /compare/pitch returns session-cached pitch timelines."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app
from tests.fixtures.audio_factory import write_wav


@pytest.fixture
def client() -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


def _inspect(client: TestClient, path: Path, role: str) -> None:
    with path.open("rb") as handle:
        response = client.post(
            "/api/v1/audio/inspect",
            data={"role": role},
            files={"file": (path.name, handle, "application/octet-stream")},
        )
    assert response.status_code == 200, response.text


def _compare_multipart(client: TestClient, guru: Path, disciple: Path) -> None:
    with guru.open("rb") as g, disciple.open("rb") as d:
        response = client.post(
            "/api/v1/compare",
            files={
                "guru_file": (guru.name, g, "audio/wav"),
                "disciple_file": (disciple.name, d, "audio/wav"),
            },
            data={"tolerance_cents": "0"},
        )
    assert response.status_code == 200, response.text
    assert "guru_pitch_frames" not in response.json()


def _get_pitch(client: TestClient) -> dict:
    response = client.get("/api/v1/compare/pitch")
    assert response.status_code == 200, response.text
    return response.json()


def test_compare_pitch_requires_inspect_cache(client: TestClient) -> None:
    response = client.get("/api/v1/compare/pitch")
    assert response.status_code == 400
    assert response.json()["error_code"] == "comparison_failed"


def test_compare_pitch_returns_frame_arrays(client: TestClient, tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.0, frequency_hz=440.0)
    disciple = write_wav(tmp_path / "disciple.wav", duration_seconds=1.2, frequency_hz=440.0)

    _inspect(client, guru, "guru")
    _inspect(client, disciple, "disciple")

    data = _get_pitch(client)
    assert len(data["guru_pitch_frames"]) > 0
    assert len(data["disciple_pitch_frames"]) > 0

    guru_frame = data["guru_pitch_frames"][0]
    assert "time_seconds" in guru_frame
    assert "voiced" in guru_frame
    assert "silent_or_unvoiced" in guru_frame


def test_inspect_compare_then_get_pitch(client: TestClient, tmp_path: Path) -> None:
    """End-to-end: inspect both roles, compare from cache, then fetch pitch for graph."""
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.0, frequency_hz=440.0)
    disciple = write_wav(tmp_path / "disciple.wav", duration_seconds=1.2, frequency_hz=440.0)

    _inspect(client, guru, "guru")
    _inspect(client, disciple, "disciple")

    compare_response = client.post("/api/v1/compare", data={"tolerance_cents": "0"})
    assert compare_response.status_code == 200, compare_response.text
    assert compare_response.json()["comparison_summary"]["match_percentage"] >= 50.0

    data = _get_pitch(client)
    assert len(data["guru_pitch_frames"]) > 0
    assert len(data["disciple_pitch_frames"]) > 0
    guru_times = [f["time_seconds"] for f in data["guru_pitch_frames"]]
    disciple_times = [f["time_seconds"] for f in data["disciple_pitch_frames"]]
    assert max(guru_times) <= 1.05
    assert max(disciple_times) <= 1.25


def test_upload_compare_then_get_pitch(client: TestClient, tmp_path: Path) -> None:
    """Multipart compare without prior inspect still populates pitch cache."""
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.0, frequency_hz=440.0)
    disciple = write_wav(tmp_path / "disciple.wav", duration_seconds=1.0, frequency_hz=440.0)

    _compare_multipart(client, guru, disciple)

    data = _get_pitch(client)
    assert len(data["guru_pitch_frames"]) > 0
    assert len(data["disciple_pitch_frames"]) > 0
