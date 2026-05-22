"""Dark theme: black background with golden-yellow accents (brand image)."""

from __future__ import annotations

# Core palette — inverted from brand art (gold on black)
COLOR_BG = "#000000"
COLOR_SURFACE = "#000000"
COLOR_ACCENT = "#EBB850"
COLOR_BORDER = COLOR_ACCENT
COLOR_TEXT = COLOR_ACCENT
COLOR_TEXT_MUTED = "#C9A44A"

# Buttons — enabled reads as raised/clickable; disabled is clearly muted
COLOR_BUTTON_ENABLED_BG = "#141414"
COLOR_BUTTON_BORDER = COLOR_ACCENT
COLOR_BUTTON_HOVER_BG = "#2a2410"
COLOR_BUTTON_HOVER_BORDER = "#F4C430"
COLOR_BUTTON_PRESSED_BG = "#0a0a0a"
COLOR_BUTTON_DISABLED_BG = "#0a0a0a"
COLOR_BUTTON_DISABLED_BORDER = "#3d3520"
COLOR_BUTTON_DISABLED_TEXT = "#5c5230"

PUSHBUTTON_STYLE = f"""
QPushButton {{
    min-height: 32px;
    min-width: 96px;
    padding: 6px 14px;
    font-size: 13px;
    border-radius: 4px;
}}
QPushButton:enabled {{
    background-color: {COLOR_BUTTON_ENABLED_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BUTTON_BORDER};
}}
QPushButton:hover:enabled {{
    background-color: {COLOR_BUTTON_HOVER_BG};
    border-color: {COLOR_BUTTON_HOVER_BORDER};
}}
QPushButton:pressed:enabled {{
    background-color: {COLOR_BUTTON_PRESSED_BG};
}}
QPushButton:disabled {{
    background-color: {COLOR_BUTTON_DISABLED_BG};
    color: {COLOR_BUTTON_DISABLED_TEXT};
    border: 1px solid {COLOR_BUTTON_DISABLED_BORDER};
}}
"""

APP_STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
}}
QLabel {{
    color: {COLOR_TEXT};
    background: transparent;
}}
{PUSHBUTTON_STYLE}
QMessageBox {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
}}
QMessageBox QLabel {{
    color: {COLOR_TEXT};
}}
QMessageBox QPushButton:enabled {{
    background-color: {COLOR_BUTTON_ENABLED_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BUTTON_BORDER};
    border-radius: 4px;
    padding: 4px 12px;
}}
QMessageBox QPushButton:disabled {{
    background-color: {COLOR_BUTTON_DISABLED_BG};
    color: {COLOR_BUTTON_DISABLED_TEXT};
    border: 1px solid {COLOR_BUTTON_DISABLED_BORDER};
}}
"""

CLUSTER_FRAME_STYLE = f"""
QFrame#BorderedCluster, QFrame#GraphCluster {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    background-color: {COLOR_SURFACE};
}}
QFrame#BorderedCluster QLabel, QFrame#GraphCluster QLabel {{
    color: {COLOR_TEXT};
    background: transparent;
}}
QFrame#GraphCluster QStackedWidget {{
    background: transparent;
}}
QFrame#BorderedCluster QPushButton {{
    min-height: 32px;
    min-width: 96px;
    padding: 6px 14px;
    font-size: 13px;
    border-radius: 4px;
}}
QFrame#BorderedCluster QPushButton:enabled {{
    background-color: {COLOR_BUTTON_ENABLED_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BUTTON_BORDER};
}}
QFrame#BorderedCluster QPushButton:hover:enabled {{
    background-color: {COLOR_BUTTON_HOVER_BG};
    border-color: {COLOR_BUTTON_HOVER_BORDER};
}}
QFrame#BorderedCluster QPushButton:pressed:enabled {{
    background-color: {COLOR_BUTTON_PRESSED_BG};
}}
QFrame#BorderedCluster QPushButton:disabled {{
    background-color: {COLOR_BUTTON_DISABLED_BG};
    color: {COLOR_BUTTON_DISABLED_TEXT};
    border: 1px solid {COLOR_BUTTON_DISABLED_BORDER};
}}
QFrame#BorderedCluster QStackedWidget {{
    background: transparent;
}}
"""

TRANSPARENT_WIDGET_STYLE = f"background: transparent; color: {COLOR_TEXT};"
MUTED_LABEL_STYLE = f"color: {COLOR_TEXT_MUTED}; background: transparent;"
TITLE_STYLE = (
    f"font-size: 18px; font-weight: bold; color: {COLOR_TEXT}; background: transparent;"
)
SUBTITLE_STYLE = f"color: {COLOR_TEXT_MUTED}; background: transparent;"
