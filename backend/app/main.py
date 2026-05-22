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
from backend.app.core.request_log import configure_logging, log_event, verbose_from_request
from backend.app.core.session import SessionManager
from backend.app.models.errors import ErrorResponse
from shared.constants import APP_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    app.state.session_manager = SessionManager()
    log_event("app", "startup", version=APP_VERSION)
    yield
    log_event("app", "shutdown")
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

    @application.middleware("http")
    async def verbose_request_middleware(request: Request, call_next):
        verbose = verbose_from_request(request)
        if verbose:
            log_event(
                "http",
                "request",
                method=request.method,
                path=request.url.path,
                query=str(request.query_params),
            )
        response = await call_next(request)
        if verbose:
            log_event(
                "http",
                "response",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )
        return response

    @application.exception_handler(HcsaError)
    async def hcsa_error_handler(request: Request, exc: HcsaError) -> JSONResponse:
        import logging

        logging.getLogger("hcsa").warning(
            "[%s] %s path=%s details=%s",
            exc.error_code,
            exc.message,
            request.url.path,
            exc.details,
        )
        return _error_response(exc)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        log_event("error", "validation_error", path=request.url.path)
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    application.include_router(health_router, prefix="/api/v1")
    application.include_router(audio_router, prefix="/api/v1")
    application.include_router(compare_router, prefix="/api/v1")

    return application


app = create_app()
