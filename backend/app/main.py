"""FastAPI application entry."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.api.routes_audio import router as audio_router
from backend.app.api.routes_compare import router as compare_router
from backend.app.api.routes_health import router as health_router
from backend.app.core.errors import HcsaError
from backend.app.core.session import SessionManager
from backend.app.models.errors import ErrorResponse
from shared.constants import APP_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.session_manager = SessionManager()
    yield
    app.state.session_manager.clear()


def _error_response(exc: HcsaError, status_code: int = 400) -> JSONResponse:
    body = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


def create_app() -> FastAPI:
    """Build the FastAPI application."""
    application = FastAPI(title="HCSA Backend", version=APP_VERSION, lifespan=lifespan)

    @application.exception_handler(HcsaError)
    async def hcsa_error_handler(_request: Request, exc: HcsaError) -> JSONResponse:
        return _error_response(exc)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    application.include_router(health_router, prefix="/api/v1")
    application.include_router(audio_router, prefix="/api/v1")
    application.include_router(compare_router, prefix="/api/v1")

    return application


app = create_app()
