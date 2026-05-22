"""Compare API and compare_service tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.services.compare_service import compare_audio_files
from tests.fixtures.audio_factory import write_wav

TARGET_HZ = 440.0
TOLERANCE_HZ = 35.0


@pytest.fixture
def client() -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


def test_compare_returns_pitch_arrays(client: TestClient, tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.5, frequency_hz=440.0)
    disciple = write_wav(tmp_path / "disciple.wav", duration_seconds=1.5, frequency_hz=466.0)

    with guru.open("rb") as g, disciple.open("rb") as d:
        response = client.post(
            "/api/v1/compare",
            files={
                "guru_file": ("guru.wav", g, "audio/wav"),
                "disciple_file": ("disciple.wav", d, "audio/wav"),
            },
        )

    assert response.status_code == 200
    data = response.json()

    assert data["guru_file_info"]["file_name"] == "guru.wav"
    assert data["disciple_file_info"]["file_name"] == "disciple.wav"
    assert "guru_sa_hz" not in data
    assert "tolerance_cents" not in data
    assert "metrics" not in data
    assert "aligned_frames" not in data

    guru_frames = data["guru_pitch_frames"]
    disciple_frames = data["disciple_pitch_frames"]
    assert len(guru_frames) > 0
    assert len(disciple_frames) > 0

    guru_voiced = [f for f in guru_frames if f["voiced"] and f["frequency_hz"]]
    assert guru_voiced
    assert abs(guru_voiced[0]["frequency_hz"] - TARGET_HZ) < TOLERANCE_HZ

    assert data["guru_summary"]["voiced_frame_count"] > 0
    assert data["disciple_summary"]["voiced_fraction"] > 0.0

    for frame in guru_frames:
        assert "cents_from_sa" not in frame
        assert "swara_label" not in frame


def test_compare_no_vocals_detected(client: TestClient, tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.5, frequency_hz=440.0)
    # Below pyin fmin (50 Hz): loads as audio but yields almost no voiced pitch frames.
    silent = write_wav(tmp_path / "disciple.wav", duration_seconds=1.5, frequency_hz=30.0)

    with guru.open("rb") as g, silent.open("rb") as d:
        response = client.post(
            "/api/v1/compare",
            files={
                "guru_file": ("guru.wav", g, "audio/wav"),
                "disciple_file": ("disciple.wav", d, "audio/wav"),
            },
        )

    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "no_vocals_detected"
    assert data["details"]["role"] == "disciple"


def test_compare_unsupported_file_type(client: TestClient, tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=0.3, frequency_hz=440.0)
    bad = tmp_path / "disciple.m4a"
    bad.write_bytes(b"\x00")

    with guru.open("rb") as g, bad.open("rb") as d:
        response = client.post(
            "/api/v1/compare",
            files={
                "guru_file": ("guru.wav", g, "audio/wav"),
                "disciple_file": ("disciple.m4a", d, "audio/mp4"),
            },
        )

    assert response.status_code == 400
    assert response.json()["error_code"] == "unsupported_file_type"


def test_compare_service_sine_contours(tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "g.wav", duration_seconds=1.5, frequency_hz=220.0)
    disciple = write_wav(tmp_path / "d.wav", duration_seconds=1.5, frequency_hz=330.0)

    result = compare_audio_files(
        guru,
        guru_file_name="g.wav",
        disciple_path=disciple,
        disciple_file_name="d.wav",
    )

    assert result.guru_pitch_frames
    assert result.disciple_pitch_frames
    assert result.guru_summary is not None
    guru_hz = next(
        f.frequency_hz for f in result.guru_pitch_frames if f.voiced and f.frequency_hz
    )
    assert guru_hz is not None
    assert abs(guru_hz - 220.0) < 40.0
