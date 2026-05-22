"""Bundled UI assets (icon, etc.)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

APP_ICON_FILENAME = "app_icon.png"
ICON_DISPLAY_SIZE = 56

_ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def app_icon_path() -> Path:
    """Path to the sitar/tabla app icon PNG."""
    return _ASSETS_DIR / APP_ICON_FILENAME


def load_app_icon_pixmap(size: int = ICON_DISPLAY_SIZE) -> QPixmap:
    """Scaled icon for the header; empty pixmap if the file is missing."""
    path = app_icon_path()
    if not path.is_file():
        return QPixmap()
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def load_app_icon() -> QIcon:
    """Window/taskbar icon."""
    path = app_icon_path()
    if path.is_file():
        return QIcon(str(path))
    return QIcon()
