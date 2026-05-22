"""Tests for verbose request logging helpers."""

from __future__ import annotations

from backend.app.core import request_log


def test_env_verbose(monkeypatch) -> None:
    monkeypatch.setenv("HCSA_VERBOSE", "1")
    assert request_log.env_verbose_enabled()
    assert request_log.should_log()


def test_verbose_off_by_default(monkeypatch) -> None:
    monkeypatch.delenv("HCSA_VERBOSE", raising=False)
    request_log.set_request_verbose(False)
    assert not request_log.should_log()
