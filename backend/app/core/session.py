"""In-memory session state and temporary file management."""

from __future__ import annotations

import shutil
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

from backend.app.models.audio import AudioFileInfo
from backend.app.models.pitch import PitchFrame

SESSION_ROOT_NAME = "hcsa-session"


@dataclass
class RoleAnalysisCache:
    """Pitch timeline and file metadata from inspect, reused at compare."""

    file_info: AudioFileInfo
    pitch_frames: list[PitchFrame]
    source_path: str


class SessionManager:
    """Tracks temp uploads, cached pitch, and comparison results for one backend run."""

    def __init__(self, temp_root: Path | None = None) -> None:
        self.session_id = str(uuid.uuid4())
        self.temp_root = temp_root or self._create_temp_root()
        self.processing_status = "idle"
        self.file_refs: dict[str, str] = {}
        self.role_file_ids: dict[str, str] = {}
        self.role_analysis: dict[str, RoleAnalysisCache] = {}
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
        self.role_analysis.clear()
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

    def set_role_analysis(
        self,
        role: str,
        *,
        file_info: AudioFileInfo,
        pitch_frames: list[PitchFrame],
        source_path: Path,
    ) -> None:
        """Store inspect pitch timeline for later compare (no re-extraction)."""
        self.role_analysis[role] = RoleAnalysisCache(
            file_info=file_info,
            pitch_frames=pitch_frames,
            source_path=str(source_path),
        )

    def get_role_analysis(self, role: str) -> RoleAnalysisCache | None:
        return self.role_analysis.get(role)

    def has_compare_ready_cache(self) -> bool:
        return "guru" in self.role_analysis and "disciple" in self.role_analysis
