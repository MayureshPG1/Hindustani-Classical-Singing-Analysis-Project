"""Bordered container for grouped control-row widgets."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

from frontend.theme import CLUSTER_FRAME_STYLE


def create_bordered_cluster(
    child: QWidget,
    *,
    parent: QWidget | None = None,
    margins: tuple[int, int, int, int] = (10, 10, 10, 10),
) -> QFrame:
    """Wrap ``child`` in a framed cluster with stable inner padding."""
    frame = QFrame(parent)
    frame.setObjectName("BorderedCluster")
    frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    frame.setStyleSheet(CLUSTER_FRAME_STYLE)

    child.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    if not child.styleSheet():
        from frontend.theme import TRANSPARENT_WIDGET_STYLE

        child.setStyleSheet(TRANSPARENT_WIDGET_STYLE)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(0)
    layout.addWidget(child)
    return frame
