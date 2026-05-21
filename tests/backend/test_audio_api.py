"""API tests for POST /audio/inspect."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app
from tests.fixtures.audio_factory import write_silence_wav, write_wav


@pytest.fixture
def client() -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


def _inspect(client: TestClient, path: Path, role: str = "guru"):
    with path.open("rb") as handle:
        return client.post(
            "/api/v1/audio/inspect",
            data={"role": role},
            files={"file": (path.name, handle, "application/octet-stream")},
        )


def test_inspect_valid_wav_returns_metadata(client: TestClient, tmp_path: Path) -> None:
    wav = write_wav(tmp_path / "guru.wav", duration_seconds=1.5, sample_rate=44100)
    response = _inspect(client, wav, role="guru")
    assert response.status_code == 200
    data = response.json()
    assert data["validation_status"] == "valid"
    assert data["file_name"] == "guru.wav"
    assert data["format"] == "wav"
    assert data["file_id"].startswith("guru-")
    assert data["error_message"] is None
    assert 1.0 <= data["duration_seconds"] <= 1.6


def test_inspect_unsupported_type(client: TestClient, tmp_path: Path) -> None:
    bad = tmp_path / "clip.m4a"
    bad.write_bytes(b"\x00\x01")
    response = _inspect(client, bad)
    assert response.status_code == 400
    assert response.json()["error_code"] == "unsupported_file_type"


def test_inspect_file_too_long(client: TestClient, tmp_path: Path) -> None:
    wav = write_wav(tmp_path / "long.wav", duration_seconds=301.0, sample_rate=22050)
    response = _inspect(client, wav)
    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == "file_too_long"
    assert body["message"] == "Audio file must be 5 minutes or shorter."
    assert body["details"]["max_duration_seconds"] == 300


def test_inspect_no_audio_detected(client: TestClient, tmp_path: Path) -> None:
    wav = write_silence_wav(tmp_path / "silent.wav", duration_seconds=0.5)
    response = _inspect(client, wav)
    assert response.status_code == 400
    assert response.json()["error_code"] == "no_audio_detected"


def test_inspect_decode_failed(client: TestClient, tmp_path: Path) -> None:
    corrupt = tmp_path / "bad.wav"
    corrupt.write_bytes(b"RIFF????")
    response = _inspect(client, corrupt)
    assert response.status_code == 400
    assert response.json()["error_code"] == "decode_failed"


def test_inspect_registers_file_in_session(client: TestClient, tmp_path: Path) -> None:
    wav = write_wav(tmp_path / "disciple.wav", duration_seconds=0.4)
    response = _inspect(client, wav, role="disciple")
    assert response.status_code == 200
    file_id = response.json()["file_id"]

    session = client.app.state.session_manager
    assert file_id in session.file_refs
    assert session.role_file_ids["disciple"] == file_id
    assert Path(session.file_refs[file_id]).exists()
