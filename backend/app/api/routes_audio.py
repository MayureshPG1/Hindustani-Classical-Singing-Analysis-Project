"""Audio inspect routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from backend.app.core.errors import raise_decode_failed, raise_unsupported_file_type
from backend.app.core.session import SessionManager
from backend.app.models.audio import AudioInspectResponse
from backend.app.services.audio_loader import (
    is_supported_file_name,
    make_file_id,
    normalize_extension,
)
from backend.app.services.inspect_service import inspect_audio_file

router = APIRouter(tags=["audio"])

ALLOWED_ROLES = frozenset({"guru", "disciple"})


def get_session(request: Request) -> SessionManager:
    return request.app.state.session_manager


@router.post("/audio/inspect", response_model=AudioInspectResponse)
async def inspect_audio(
    file: UploadFile = File(...),
    role: str = Form(...),
    session: SessionManager = Depends(get_session),
) -> AudioInspectResponse:
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
    content = await file.read()
    if not content:
        raise_decode_failed(file_name, "empty upload")

    dest.write_bytes(content)

    result = inspect_audio_file(dest, role=role, file_name=file_name, file_id=file_id)
    session.set_role_file(role, result.file_info.file_id, dest)
    return result
