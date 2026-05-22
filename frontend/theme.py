"""Dark theme styles matching the desktop shell."""

from __future__ import annotations

# Core palette (dark shell — black background, light text)
COLOR_BG = "#000000"
COLOR_SURFACE = "#000000"
COLOR_BORDER = "#505050"
COLOR_TEXT = "#ececec"
COLOR_TEXT_MUTED = "#a8a8a8"
COLOR_BUTTON_BG = "#2d2d2d"
COLOR_BUTTON_BORDER = "#5c5c5c"
COLOR_BUTTON_HOVER = "#3a3a3a"
COLOR_BUTTON_DISABLED_TEXT = "#6e6e6e"

APP_STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
}}
QLabel {{
    color: {COLOR_TEXT};
    background: transparent;
}}
QPushButton {{
    background-color: {COLOR_BUTTON_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BUTTON_BORDER};
    border-radius: 4px;
    padding: 6px 12px;
}}
QPushButton:hover:enabled {{
    background-color: {COLOR_BUTTON_HOVER};
}}
QPushButton:disabled {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_BUTTON_DISABLED_TEXT};
    border-color: {COLOR_BORDER};
}}
"""

CLUSTER_FRAME_STYLE = f"""
QFrame#BorderedCluster {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    background-color: {COLOR_SURFACE};
}}
QFrame#BorderedCluster QLabel {{
    color: {COLOR_TEXT};
    background: transparent;
}}
QFrame#BorderedCluster QPushButton {{
    background-color: {COLOR_BUTTON_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BUTTON_BORDER};
    border-radius: 4px;
    padding: 6px 12px;
}}
QFrame#BorderedCluster QPushButton:hover:enabled {{
    background-color: {COLOR_BUTTON_HOVER};
}}
QFrame#BorderedCluster QPushButton:disabled {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_BUTTON_DISABLED_TEXT};
    border-color: {COLOR_BORDER};
}}
QFrame#BorderedCluster QStackedWidget {{
    background: transparent;
}}
"""

TRANSPARENT_WIDGET_STYLE = "background: transparent; color: #ececec;"
MUTED_LABEL_STYLE = f"color: {COLOR_TEXT_MUTED}; background: transparent;"
TITLE_STYLE = "font-size: 18px; font-weight: bold; color: #ececec; background: transparent;"
SUBTITLE_STYLE = f"color: {COLOR_TEXT_MUTED}; background: transparent;"
