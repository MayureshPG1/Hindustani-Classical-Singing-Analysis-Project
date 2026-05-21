"""Unit tests for swara_mapper."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.core import config
from backend.app.models.comparison import PitchFrame
from backend.app.services.audio_loader import load_and_validate
from backend.app.services.pitch_extractor import extract_pitch
from backend.app.services.sa_detector import detect_sa, hz_to_cents_from_sa
from backend.app.services.swara_mapper import (
    annotate_pitch_frames,
    detect_sa_and_annotate,
    get_swara_table,
    map_cents_to_swara,
    swara_f0_hz,
)
from shared.constants import SWARA_TABLE
from tests.fixtures.audio_factory import write_wav


@pytest.mark.parametrize(
    ("cents", "symbol", "label"),
    [
        (0, "S", "Sa"),
        (100, "r", "Komal Re"),
        (200, "R", "Shuddha Re"),
        (300, "g", "Komal Ga"),
        (400, "G", "Shuddha Ga"),
        (500, "m", "Shuddha Ma"),
        (600, "M", "Tivra Ma"),
        (700, "P", "Pa"),
        (800, "d", "Komal Dha"),
        (900, "D", "Shuddha Dha"),
        (1000, "n", "Komal Ni"),
        (1100, "N", "Shuddha Ni"),
    ],
)
def test_map_cents_to_swara_symbols(cents: float, symbol: str, label: str) -> None:
    swara = map_cents_to_swara(cents)
    assert swara.symbol == symbol
    assert swara.label == label
    assert swara.cents_from_sa == cents


def test_get_swara_table_matches_shared_constants() -> None:
    table = get_swara_table()
    assert len(table) == 12
    assert table[0].symbol == SWARA_TABLE[0]["symbol"]
    assert table[-1].symbol == SWARA_TABLE[-1]["symbol"]


def test_swara_f0_hz_from_sa() -> None:
    sa_hz = 200.0
    pa_hz = swara_f0_hz(sa_hz, 700.0)
    assert pa_hz == pytest.approx(sa_hz * (2.0 ** (700.0 / 1200.0)), rel=1e-6)


def test_annotate_pitch_frames_sets_sa_on_all_frames() -> None:
    frames = [
        PitchFrame(
            time_seconds=0.0,
            frequency_hz=220.0,
            confidence=0.9,
            voiced=True,
            silent_or_unvoiced=False,
        ),
        PitchFrame(
            time_seconds=0.1,
            frequency_hz=None,
            confidence=0.1,
            voiced=False,
            silent_or_unvoiced=True,
        ),
    ]
    sa_hz = 220.0
    annotated = annotate_pitch_frames(frames, sa_hz)

    assert all(frame.sa_f0_hz == sa_hz for frame in annotated)
    assert annotated[0].cents_from_sa == pytest.approx(0.0, abs=5.0)
    assert annotated[0].swara_symbol == "S"
    assert annotated[0].swara_label == "Sa"
    assert annotated[0].swara_f0_hz == pytest.approx(sa_hz, rel=1e-6)
    assert annotated[1].cents_from_sa is None
    assert annotated[1].swara_symbol is None


def test_detect_sa_and_annotate_integration(tmp_path: Path) -> None:
    path = write_wav(
        tmp_path / "sa.wav",
        duration_seconds=2.0,
        sample_rate=config.SR,
        frequency_hz=261.63,
        amplitude=0.6,
    )
    loaded = load_and_validate(path, role="guru", file_name="sa.wav")
    frames = extract_pitch(loaded.waveform, sample_rate=loaded.sample_rate)

    annotated, result = detect_sa_and_annotate(frames)
    voiced = [frame for frame in annotated if frame.voiced]

    assert result.sa_hz > 0
    assert voiced
    assert all(frame.sa_f0_hz == result.sa_hz for frame in annotated)
    assert all(frame.cents_from_sa is not None for frame in voiced)
    assert all(frame.swara_symbol for frame in voiced)


def test_relative_cents_wrap_to_nearest_swara() -> None:
    """Cents above one octave still map via modulo 1200."""
    swara = map_cents_to_swara(1300.0)
    assert swara.symbol == "r"
    assert swara.cents_from_sa == 100.0
