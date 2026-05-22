"""Audio inspect routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from backend.app.core.errors import raise_decode_failed, raise_unsupported_file_type
from backend.app.core.request_log import log_event, log_step
from backend.app.core.session import SessionManager
from backend.app.models.audio import AudioInspectResponse
from backend.app.services.audio_loader import (
    is_supported_file_name,
    make_file_id,
    normalize_extension,
)
from backend.app.services.inspect_service import inspect_audio_file

router = APIRouter(tags=["audio"])
ROUTE = "POST /audio/inspect"

ALLOWED_ROLES = frozenset({"guru", "disciple"})


def get_session(request: Request) -> SessionManager:
    return request.app.state.session_manager


@router.post("/audio/inspect", response_model=AudioInspectResponse)
async def inspect_audio(
    request: Request,
    file: UploadFile = File(...),
    role: str = Form(...),
    session: SessionManager = Depends(get_session),
) -> AudioInspectResponse:
    log_event(ROUTE, "called", role=role, filename=file.filename)

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=422,
            detail=f"role must be one of: {', '.join(sorted(ALLOWED_ROLES))}",
        )

    file_name = file.filename or "upload"
    if not is_supported_file_name(file_name):
        raise_unsupported_file_type(file_name)

    file_id = make_file_id(role)
    dest = session.temp_root / f"{file_id}{normalize_extension(file_name)}"

    with log_step(ROUTE, "read upload", file_name=file_name, role=role):
        content = await file.read()
    if not content:
        raise_decode_failed(file_name, "empty upload")

    dest.write_bytes(content)
    log_event(ROUTE, "saved temp file", path=str(dest), bytes=len(content))

    with log_step(ROUTE, "inspect_audio_file", file_id=file_id):
        result = inspect_audio_file(dest, role=role, file_name=file_name, file_id=file_id)

    session.set_role_file(role, result.file_info.file_id, dest)
    log_event(
        ROUTE,
        "success",
        file_id=result.file_info.file_id,
        duration_s=result.file_info.duration_seconds,
        preview_frames=len(result.pitch_metadata.preview_frames),
        total_frames=result.pitch_metadata.total_frame_count,
        voiced_fraction=result.pitch_metadata.voiced_fraction,
    )
    return result
