"""Health check routes."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.models.comparison import HealthResponse
from shared.constants import APP_VERSION

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version=APP_VERSION)
