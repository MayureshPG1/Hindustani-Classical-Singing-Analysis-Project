"""Compare API and compare_service tests (summary metrics, wall-clock Hz)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.models.pitch import PitchFrame
from backend.app.services.compare_service import compare_audio_files
from backend.app.services.scorer import deviation_cents, score_wall_clock
from tests.fixtures.audio_factory import write_wav


@pytest.fixture
def client() -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


def test_compare_returns_comparison_summary(client: TestClient, tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.5, frequency_hz=440.0)
    disciple = write_wav(tmp_path / "disciple.wav", duration_seconds=1.5, frequency_hz=440.0)

    with guru.open("rb") as g, disciple.open("rb") as d:
        response = client.post(
            "/api/v1/compare",
            files={
                "guru_file": ("guru.wav", g, "audio/wav"),
                "disciple_file": ("disciple.wav", d, "audio/wav"),
            },
            data={"tolerance_cents": "10"},
        )

    assert response.status_code == 200
    data = response.json()

    assert data["guru_file_info"]["file_name"] == "guru.wav"
    assert data["disciple_file_info"]["file_name"] == "disciple.wav"
    assert "guru_pitch_frames" not in data
    assert "disciple_pitch_frames" not in data
    assert "guru_summary" not in data

    summary = data["comparison_summary"]
    assert summary["tolerance_cents"] == 10
    assert summary["match_percentage"] >= 50.0
    assert summary["overall_score"] == summary["match_percentage"]
    assert summary["match_percentage"] + summary["higher_percentage"] + summary["lower_percentage"] == pytest.approx(
        100.0, abs=0.1
    )
    assert summary["average_deviation_cents"] >= 0.0


def test_compare_detuned_disciple_has_deviation(client: TestClient, tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.5, frequency_hz=440.0)
    disciple = write_wav(tmp_path / "disciple.wav", duration_seconds=1.5, frequency_hz=466.0)

    with guru.open("rb") as g, disciple.open("rb") as d:
        response = client.post(
            "/api/v1/compare",
            files={
                "guru_file": ("guru.wav", g, "audio/wav"),
                "disciple_file": ("disciple.wav", d, "audio/wav"),
            },
            data={"tolerance_cents": "0"},
        )

    assert response.status_code == 200
    summary = response.json()["comparison_summary"]
    assert summary["average_deviation_cents"] > 20.0
    assert summary["match_percentage"] < 90.0


def test_compare_invalid_tolerance(client: TestClient, tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.0, frequency_hz=440.0)
    disciple = write_wav(tmp_path / "disciple.wav", duration_seconds=1.0, frequency_hz=440.0)

    with guru.open("rb") as g, disciple.open("rb") as d:
        response = client.post(
            "/api/v1/compare",
            files={
                "guru_file": ("guru.wav", g, "audio/wav"),
                "disciple_file": ("disciple.wav", d, "audio/wav"),
            },
            data={"tolerance_cents": "30"},
        )

    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_tolerance"


def test_compare_no_vocals_detected(client: TestClient, tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "guru.wav", duration_seconds=1.5, frequency_hz=440.0)
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
    bad = tmp_path / "disciple.flac"
    bad.write_bytes(b"\x00")

    with guru.open("rb") as g, bad.open("rb") as d:
        response = client.post(
            "/api/v1/compare",
            files={
                "guru_file": ("guru.wav", g, "audio/wav"),
                "disciple_file": ("disciple.flac", d, "audio/flac"),
            },
        )

    assert response.status_code == 400
    assert response.json()["error_code"] == "unsupported_file_type"


def test_compare_service_same_pitch_high_match(tmp_path: Path) -> None:
    guru = write_wav(tmp_path / "g.wav", duration_seconds=1.5, frequency_hz=220.0)
    disciple = write_wav(tmp_path / "d.wav", duration_seconds=1.5, frequency_hz=220.0)

    result, guru_frames, disciple_frames = compare_audio_files(
        guru,
        guru_file_name="g.wav",
        disciple_path=disciple,
        disciple_file_name="d.wav",
        tolerance_cents=10,
    )

    assert len(guru_frames) > 0
    assert len(disciple_frames) > 0
    assert result.comparison_summary.match_percentage >= 50.0
    assert result.comparison_summary.tolerance_cents == 10


def test_scorer_deviation_cents() -> None:
    assert deviation_cents(440.0, 440.0) == pytest.approx(0.0, abs=0.01)
    ratio_cents = deviation_cents(440.0, 466.0)
    assert ratio_cents > 90.0


def test_scorer_wall_clock_pairing() -> None:
    guru = [
        PitchFrame(time_seconds=0.0, frequency_hz=440.0, voiced=True, silent_or_unvoiced=False),
        PitchFrame(time_seconds=0.1, frequency_hz=440.0, voiced=True, silent_or_unvoiced=False),
    ]
    disciple = [
        PitchFrame(time_seconds=0.0, frequency_hz=440.0, voiced=True, silent_or_unvoiced=False),
        PitchFrame(time_seconds=0.1, frequency_hz=450.0, voiced=True, silent_or_unvoiced=False),
    ]
    summary = score_wall_clock(
        guru,
        disciple,
        tolerance_cents=5,
        guru_duration_seconds=1.0,
        disciple_duration_seconds=1.0,
    )
    assert summary.match_percentage + summary.higher_percentage + summary.lower_percentage == pytest.approx(
        100.0
    )
