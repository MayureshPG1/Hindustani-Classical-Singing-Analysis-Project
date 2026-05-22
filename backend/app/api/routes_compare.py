"""Session and compare routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from backend.app.core.errors import raise_comparison_failed, raise_decode_failed, raise_unsupported_file_type
from backend.app.core.request_log import log_event, log_step
from backend.app.core.session import SessionManager
from backend.app.models.comparison import ClearSessionResponse, ComparisonResult
from backend.app.services.audio_loader import (
    is_supported_file_name,
    make_file_id,
    normalize_extension,
)
from backend.app.services.compare_service import (
    compare_audio_files,
    compare_from_analysis_cache,
    validate_tolerance_cents,
)
from shared.constants import DEFAULT_TOLERANCE_CENTS

router = APIRouter(tags=["compare"])


def get_session(request: Request) -> SessionManager:
    return request.app.state.session_manager


@router.post("/session/clear", response_model=ClearSessionResponse)
def clear_session(request: Request, session: SessionManager = Depends(get_session)) -> ClearSessionResponse:
    log_event("POST /session/clear", "called", session_id=session.session_id)
    session.clear()
    log_event("POST /session/clear", "cleared")
    return ClearSessionResponse()


@router.post("/compare", response_model=ComparisonResult)
async def compare_recordings(
    request: Request,
    guru_file: UploadFile | None = File(None),
    disciple_file: UploadFile | None = File(None),
    tolerance_cents: int = Form(DEFAULT_TOLERANCE_CENTS),
    session: SessionManager = Depends(get_session),
) -> ComparisonResult:
    validate_tolerance_cents(tolerance_cents)
    log_event("POST /compare", "called", tolerance_cents=tolerance_cents)

    if session.has_compare_ready_cache():
        guru_cache = session.get_role_analysis("guru")
        disciple_cache = session.get_role_analysis("disciple")
        if guru_cache is None or disciple_cache is None:
            raise_comparison_failed("Cached pitch data is incomplete.")
        log_event(
            "POST /compare",
            "using cached pitch from inspect",
            guru_file_id=guru_cache.file_info.file_id,
            disciple_file_id=disciple_cache.file_info.file_id,
        )
        session.processing_status = "generating_graph"
        try:
            with log_step("POST /compare", "compare_from_analysis_cache"):
                result = compare_from_analysis_cache(
                    guru_cache,
                    disciple_cache,
                    tolerance_cents=tolerance_cents,
                )
        finally:
            session.processing_status = "idle"
        session.cached_comparison = result
        summary = result.comparison_summary
        log_event(
            "POST /compare",
            "success (cached)",
            overall_score=summary.overall_score,
            match_percentage=summary.match_percentage,
            tolerance_cents=summary.tolerance_cents,
        )
        return result

    if guru_file is None or disciple_file is None:
        raise_comparison_failed(
            "Inspect guru and disciple audio before comparing, or upload both files."
        )

    guru_name = guru_file.filename or "guru"
    disciple_name = disciple_file.filename or "disciple"

    for file_name in (guru_name, disciple_name):
        if not is_supported_file_name(file_name):
            raise_unsupported_file_type(file_name)

    guru_id = make_file_id("guru")
    disciple_id = make_file_id("disciple")
    guru_dest = session.temp_root / f"{guru_id}{normalize_extension(guru_name)}"
    disciple_dest = session.temp_root / f"{disciple_id}{normalize_extension(disciple_name)}"

    with log_step("POST /compare", "read uploads"):
        guru_bytes = await guru_file.read()
        disciple_bytes = await disciple_file.read()

    if not guru_bytes:
        raise_decode_failed(guru_name, "empty upload")
    if not disciple_bytes:
        raise_decode_failed(disciple_name, "empty upload")

    guru_dest.write_bytes(guru_bytes)
    disciple_dest.write_bytes(disciple_bytes)
    log_event(
        "POST /compare",
        "saved temp files (no inspect cache)",
        guru_bytes=len(guru_bytes),
        disciple_bytes=len(disciple_bytes),
    )

    session.processing_status = "loading_audio"
    try:
        with log_step("POST /compare", "compare_audio_files"):
            result = compare_audio_files(
                guru_dest,
                guru_file_name=guru_name,
                guru_file_id=guru_id,
                disciple_path=disciple_dest,
                disciple_file_name=disciple_name,
                disciple_file_id=disciple_id,
                tolerance_cents=tolerance_cents,
            )
    finally:
        session.processing_status = "idle"

    session.set_role_file("guru", result.guru_file_info.file_id, guru_dest)
    session.set_role_file("disciple", result.disciple_file_info.file_id, disciple_dest)
    session.cached_comparison = result

    summary = result.comparison_summary
    log_event(
        "POST /compare",
        "success",
        overall_score=summary.overall_score,
        match_percentage=summary.match_percentage,
        tolerance_cents=summary.tolerance_cents,
    )
    return result
