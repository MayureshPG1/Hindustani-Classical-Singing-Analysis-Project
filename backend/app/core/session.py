"""In-memory session state and temporary file management."""

from __future__ import annotations

import shutil
import tempfile
import uuid
from pathlib import Path

SESSION_ROOT_NAME = "hcsa-session"


class SessionManager:
    """Tracks temp uploads and cached comparison for one backend run."""

    def __init__(self, temp_root: Path | None = None) -> None:
        self.session_id = str(uuid.uuid4())
        self.temp_root = temp_root or self._create_temp_root()
        self.processing_status = "idle"
        self.file_refs: dict[str, str] = {}
        self.role_file_ids: dict[str, str] = {}
        self.cached_comparison: object | None = None

    @staticmethod
    def _create_temp_root() -> Path:
        path = Path(tempfile.gettempdir()) / SESSION_ROOT_NAME / str(uuid.uuid4())
        path.mkdir(parents=True, exist_ok=True)
        return path

    def clear(self) -> None:
        """Delete temp files and drop cached state."""
        if self.temp_root.exists():
            shutil.rmtree(self.temp_root, ignore_errors=True)
        self.temp_root = self._create_temp_root()
        self.processing_status = "idle"
        self.file_refs.clear()
        self.role_file_ids.clear()
        self.cached_comparison = None

    def register_temp_file(self, file_id: str, path: Path) -> None:
        self.file_refs[file_id] = str(path)

    def set_role_file(self, role: str, file_id: str, path: Path) -> None:
        """Register an upload, replacing any prior file for the same role."""
        previous_id = self.role_file_ids.get(role)
        if previous_id and previous_id in self.file_refs:
            previous_path = Path(self.file_refs[previous_id])
            if previous_path.exists():
                previous_path.unlink(missing_ok=True)
            del self.file_refs[previous_id]
        self.role_file_ids[role] = file_id
        self.register_temp_file(file_id, path)
