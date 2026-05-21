"""FastAPI application entry (routes wired in Phase 1)."""

from __future__ import annotations

from fastapi import FastAPI

from shared.constants import APP_VERSION


def create_app() -> FastAPI:
    """Build the FastAPI application."""
    return FastAPI(title="HCSA Backend", version=APP_VERSION)


app = create_app()
