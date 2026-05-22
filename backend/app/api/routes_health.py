"""Health check routes."""

from __future__ import annotations

from fastapi import APIRouter, Request

from backend.app.core.request_log import log_event
from backend.app.models.comparison import HealthResponse
from shared.constants import APP_VERSION

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    log_event("GET /health", "ok", version=APP_VERSION)
    return HealthResponse(status="ok", version=APP_VERSION)
