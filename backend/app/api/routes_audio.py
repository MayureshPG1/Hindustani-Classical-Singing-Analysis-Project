"""Audio inspect routes."""

from __future__ import annotations

import logging
import time
import traceback
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from backend.app.core import config
from backend.app.core.errors import HcsaError, raise_unsupported_file_type
from backend.app.core.session import SessionManager
from backend.app.models.comparison import (
    AudioInspectResponse,
    SaDetectionMetadata,
)
from backend.app.services.audio_loader import (
    is_supported_file_name,
    load_and_validate,
    make_file_id,
    normalize_extension,
)
from backend.app.services.pitch_extractor import extract_pitch
from backend.app.services.swara_mapper import detect_sa_and_annotate

router = APIRouter(tags=["audio"])
logger = logging.getLogger("hcsa.inspect")

ALLOWED_ROLES = frozenset({"guru", "disciple"})


def get_session(request: Request) -> SessionManager:
    return request.app.state.session_manager


def _log_step(step: str, started: float, **extra: object) -> float:
    elapsed = time.perf_counter() - started
    details = " ".join(f"{key}={value}" for key, value in extra.items())
    suffix = f" ({details})" if details else ""
    logger.info("[inspect] %s done in %.2fs%s", step, elapsed, suffix)
    return time.perf_counter()


@router.post("/audio/inspect", response_model=AudioInspectResponse)
async def inspect_audio(
    file: UploadFile = File(...),
    role: str = Form(...),
    session: SessionManager = Depends(get_session),
) -> AudioInspectResponse:
    request_started = time.perf_counter()
    logger.info(
        "[inspect] START role=%s filename=%s content_type=%s",
        role,
        file.filename,
        file.content_type,
    )

    try:
        if role not in ALLOWED_ROLES:
            logger.warning("[inspect] invalid role=%s", role)
            raise HTTPException(
                status_code=422,
                detail=f"role must be one of: {', '.join(sorted(ALLOWED_ROLES))}",
            )

        file_name = file.filename or "upload"
        if not is_supported_file_name(file_name):
            logger.warning("[inspect] unsupported file_name=%s", file_name)
            raise_unsupported_file_type(file_name)

        suffix = normalize_extension(file_name)
        file_id = make_file_id(role)
        dest = session.temp_root / f"{file_id}{suffix}"
        logger.info("[inspect] temp dest=%s file_id=%s", dest, file_id)

        step_started = time.perf_counter()
        logger.info("[inspect] reading upload bytes...")
        content = await file.read()
        step_started = _log_step("read_upload", step_started, bytes=len(content))

        if not content:
            from backend.app.core.errors import raise_decode_failed

            logger.warning("[inspect] empty upload for file_name=%s", file_name)
            raise_decode_failed(file_name, "empty upload")

        logger.info("[inspect] writing %s bytes to disk...", len(content))
        dest.write_bytes(content)
        step_started = _log_step("write_temp_file", step_started, path=str(dest))

        logger.info("[inspect] load_and_validate starting...")
        loaded = load_and_validate(dest, role=role, file_name=file_name, file_id=file_id)
        step_started = _log_step(
            "load_and_validate",
            step_started,
            duration_seconds=loaded.file_info.duration_seconds,
            waveform_samples=len(loaded.waveform),
            sample_rate=loaded.sample_rate,
        )

        logger.info("[inspect] extract_pitch starting (this can take a while on long files)...")
        pitch_frames = extract_pitch(loaded.waveform, sample_rate=loaded.sample_rate)
        voiced_count = sum(1 for frame in pitch_frames if frame.voiced)
        step_started = _log_step(
            "extract_pitch",
            step_started,
            total_frames=len(pitch_frames),
            voiced_frames=voiced_count,
        )

        logger.info("[inspect] detect_sa_and_annotate starting...")
        annotated_frames, sa_result = detect_sa_and_annotate(pitch_frames)
        step_started = _log_step(
            "detect_sa_and_annotate",
            step_started,
            sa_hz=round(sa_result.sa_hz, 2),
            sa_confidence=round(sa_result.confidence, 4),
            annotated_frames=len(annotated_frames),
        )

        session.set_role_file(role, loaded.file_info.file_id, dest)
        _log_step("session_register", step_started, role=role, file_id=file_id)

        preview_count = config.INSPECT_PITCH_FRAME_PREVIEW_COUNT
        pitch_preview = annotated_frames[:preview_count]
        response = AudioInspectResponse(
            file_info=loaded.file_info,
            sa=SaDetectionMetadata(
                sa_hz=sa_result.sa_hz,
                confidence=sa_result.confidence,
            ),
            pitch_frames=pitch_preview,
        )
        logger.info(
            "[inspect] SUCCESS total_time=%.2fs pitch_frames_total=%s pitch_frames_returned=%s sa_hz=%.2f",
            time.perf_counter() - request_started,
            len(annotated_frames),
            len(pitch_preview),
            sa_result.sa_hz,
        )
        return response

    except HcsaError:
        logger.error(
            "[inspect] FAILED (HcsaError) after %.2fs — see hcsa.api log above",
            time.perf_counter() - request_started,
        )
        raise
    except Exception:
        logger.error(
            "[inspect] FAILED (unexpected) after %.2fs:\n%s",
            time.perf_counter() - request_started,
            traceback.format_exc(),
        )
        raise
