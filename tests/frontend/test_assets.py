"""Bundled frontend asset tests."""

from __future__ import annotations

from frontend.assets import app_icon_path, load_app_icon_pixmap


def test_app_icon_exists_and_loads() -> None:
    path = app_icon_path()
    assert path.is_file()
    pixmap = load_app_icon_pixmap()
    assert not pixmap.isNull()
    assert pixmap.width() > 0
    assert pixmap.height() > 0
