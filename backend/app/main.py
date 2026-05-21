"""FastAPI application entry."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.api.routes_audio import router as audio_router
from backend.app.api.routes_compare import router as compare_router
from backend.app.api.routes_health import router as health_router
from backend.app.core.errors import HcsaError, INVALID_TOLERANCE_MESSAGE
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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )

    application = FastAPI(title="HCSA Backend", version=APP_VERSION, lifespan=lifespan)

    @application.exception_handler(HcsaError)
    async def hcsa_error_handler(request: Request, exc: HcsaError) -> JSONResponse:
        logging.getLogger("hcsa.api").error(
            "HcsaError on %s %s: code=%s message=%s details=%s",
            request.method,
            request.url.path,
            exc.error_code,
            exc.message,
            exc.details,
        )
        return _error_response(exc)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        if request.url.path.endswith("/settings/tolerance"):
            details: dict = {}
            for err in exc.errors():
                loc = err.get("loc", ())
                if "tolerance_cents" in loc:
                    details["tolerance_cents"] = err.get("input")
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error_code="invalid_tolerance",
                    message=INVALID_TOLERANCE_MESSAGE,
                    details=details or {"errors": exc.errors()},
                ).model_dump(),
            )
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    application.include_router(health_router, prefix="/api/v1")
    application.include_router(audio_router, prefix="/api/v1")
    application.include_router(compare_router, prefix="/api/v1")

    return application


app = create_app()
