"""In-memory session state and temporary file management."""

from __future__ import annotations

import shutil
import tempfile
import uuid
from pathlib import Path

from backend.app.models.comparison import ToleranceSettings
from shared.constants import (
    DEFAULT_TOLERANCE_CENTS,
    MAX_TOLERANCE_CENTS,
    MIN_TOLERANCE_CENTS,
    TOLERANCE_STEP_CENTS,
)

SESSION_ROOT_NAME = "hcsa-session"


class SessionManager:
    """Tracks tolerance, temp uploads, and cached analysis for one backend run."""

    def __init__(self, temp_root: Path | None = None) -> None:
        self.session_id = str(uuid.uuid4())
        self.temp_root = temp_root or self._create_temp_root()
        self.tolerance_cents = DEFAULT_TOLERANCE_CENTS
        self.processing_status = "idle"
        self.file_refs: dict[str, str] = {}
        self.role_file_ids: dict[str, str] = {}
        self.cached_comparison: object | None = None

    @staticmethod
    def _create_temp_root() -> Path:
        path = Path(tempfile.gettempdir()) / SESSION_ROOT_NAME / str(uuid.uuid4())
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_tolerance_settings(self) -> ToleranceSettings:
        return ToleranceSettings(
            tolerance_cents=self.tolerance_cents,
            default_tolerance_cents=DEFAULT_TOLERANCE_CENTS,
            step_cents=TOLERANCE_STEP_CENTS,
            minimum_tolerance_cents=MIN_TOLERANCE_CENTS,
            maximum_tolerance_cents=MAX_TOLERANCE_CENTS,
        )

    def set_tolerance_cents(self, value: float) -> ToleranceSettings:
        self.tolerance_cents = value
        return self.get_tolerance_settings()

    def clear(self) -> None:
        """Delete temp files, reset tolerance, and drop cached state."""
        if self.temp_root.exists():
            shutil.rmtree(self.temp_root, ignore_errors=True)
        self.temp_root = self._create_temp_root()
        self.tolerance_cents = DEFAULT_TOLERANCE_CENTS
        self.processing_status = "idle"
        self.file_refs.clear()
        self.role_file_ids.clear()
        self.cached_comparison = None

    def register_temp_file(self, file_id: str, path: Path) -> None:
        self.file_refs[file_id] = str(path)

    def set_role_file(self, role: str, file_id: str, path: Path) -> None:
        """Register an inspected upload, replacing any prior file for the same role."""
        previous_id = self.role_file_ids.get(role)
        if previous_id and previous_id in self.file_refs:
            previous_path = Path(self.file_refs[previous_id])
            if previous_path.exists():
                previous_path.unlink(missing_ok=True)
            del self.file_refs[previous_id]
        self.role_file_ids[role] = file_id
        self.register_temp_file(file_id, path)
