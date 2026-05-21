"""Settings, session, compare, and swara routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.app.core.errors import validate_tolerance_cents
from backend.app.core.session import SessionManager
from backend.app.models.comparison import (
    ClearSessionResponse,
    ToleranceSettings,
    ToleranceUpdateRequest,
)
from backend.app.models.swara import SwaraMapResponse
from backend.app.services.swara_mapper import get_swara_table

router = APIRouter(tags=["settings"])


def get_session(request: Request) -> SessionManager:
    return request.app.state.session_manager


@router.get("/settings/tolerance", response_model=ToleranceSettings)
def get_tolerance(session: SessionManager = Depends(get_session)) -> ToleranceSettings:
    return session.get_tolerance_settings()


@router.put("/settings/tolerance", response_model=ToleranceSettings)
def set_tolerance(
    body: ToleranceUpdateRequest,
    session: SessionManager = Depends(get_session),
) -> ToleranceSettings:
    cents = validate_tolerance_cents(body.tolerance_cents)
    return session.set_tolerance_cents(cents)


@router.post("/session/clear", response_model=ClearSessionResponse)
def clear_session(session: SessionManager = Depends(get_session)) -> ClearSessionResponse:
    session.clear()
    return ClearSessionResponse()


@router.get("/swara-map", response_model=SwaraMapResponse)
def swara_map() -> SwaraMapResponse:
    return SwaraMapResponse(items=get_swara_table())
