"""Console logging for API routes when verbose mode is enabled."""

from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

from fastapi import Request

_logger = logging.getLogger("hcsa")
_configured = False

_verbose_ctx: ContextVar[bool] = ContextVar("hcsa_verbose", default=False)


def configure_logging() -> None:
    """Attach a stdout handler once; level follows HCSA_VERBOSE env."""
    global _configured
    if _configured:
        return
    _configured = True

    level = logging.DEBUG if env_verbose_enabled() else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] hcsa: %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )
    _logger.setLevel(level)


def env_verbose_enabled() -> bool:
    return os.environ.get("HCSA_VERBOSE", "").strip().lower() in ("1", "true", "yes", "on")


def is_verbose(request: Request | None = None) -> bool:
    """True when env, query ?verbose=true, or header X-HCSA-Verbose is set."""
    if env_verbose_enabled():
        return True
    if request is not None:
        if request.query_params.get("verbose", "").strip().lower() in ("1", "true", "yes", "on"):
            return True
        if request.headers.get("x-hcsa-verbose", "").strip().lower() in ("1", "true", "yes", "on"):
            return True
    return _verbose_ctx.get()


def set_request_verbose(enabled: bool) -> None:
    _verbose_ctx.set(enabled)


def verbose_from_request(request: Request) -> bool:
    enabled = is_verbose(request)
    set_request_verbose(enabled)
    return enabled


def should_log() -> bool:
    return is_verbose() or env_verbose_enabled()


def log_event(route: str, message: str, **fields: Any) -> None:
    if not should_log():
        return
    if fields:
        extras = " ".join(f"{key}={value!r}" for key, value in fields.items())
        _logger.info("[%s] %s | %s", route, message, extras)
    else:
        _logger.info("[%s] %s", route, message)


@contextmanager
def log_step(route: str, step: str, **fields: Any) -> Iterator[None]:
    """Log step start/end and elapsed seconds when verbose."""
    if not should_log():
        yield
        return
    log_event(route, f"{step} start", **fields)
    started = time.perf_counter()
    try:
        yield
    except Exception as exc:
        elapsed = time.perf_counter() - started
        log_event(route, f"{step} failed", error=type(exc).__name__, elapsed_s=round(elapsed, 3))
        raise
    else:
        elapsed = time.perf_counter() - started
        log_event(route, f"{step} done", elapsed_s=round(elapsed, 3), **fields)
