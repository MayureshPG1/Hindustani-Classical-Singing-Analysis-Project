"""Session pitch cache: inspect stores timelines; compare reuses them."""

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


def test_inspect_stores_pitch_in_session(client: TestClient, tmp_path: Path) -> None:
    wav = write_wav(tmp_path / "guru.wav", duration_seconds=1.0, frequency_hz=440.0)
    _inspect(client, wav, "guru")

    session = client.app.state.session_manager
    cache = session.get_role_analysis("guru")
    assert cache is not None
    assert cache.file_info.file_name == "guru.wav"
    assert len(cache.pitch_frames) > 0
    assert cache.pitch_frames[0].time_seconds >= 0.0


def test_compare_after_inspect_reuses_cached_pitch(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.2, frequency_hz=440.0)
    disciple = write_wav(tmp_path / "disciple.wav", duration_seconds=1.2, frequency_hz=440.0)

    from backend.app.services import compare_service, inspect_service
    from backend.app.services.pitch_extractor import extract_pitch as real_extract

    extract_calls = 0

    def counting_extract(*args, **kwargs):
        nonlocal extract_calls
        extract_calls += 1
        return real_extract(*args, **kwargs)

    monkeypatch.setattr(inspect_service, "extract_pitch", counting_extract)
    monkeypatch.setattr(compare_service, "extract_pitch", counting_extract)

    _inspect(client, guru, "guru")
    _inspect(client, disciple, "disciple")
    assert extract_calls == 2

    response = client.post(
        "/api/v1/compare",
        data={"tolerance_cents": "0"},
    )
    assert response.status_code == 200, response.text
    assert extract_calls == 2
    summary = response.json()["comparison_summary"]
    assert summary["match_percentage"] >= 50.0


def test_compare_without_inspect_requires_uploads(client: TestClient) -> None:
    response = client.post("/api/v1/compare", data={"tolerance_cents": "0"})
    assert response.status_code == 400
    assert response.json()["error_code"] == "comparison_failed"
