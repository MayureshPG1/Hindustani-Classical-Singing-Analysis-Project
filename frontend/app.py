"""Desktop application entry point."""

from __future__ import annotations


def main() -> None:
    """Launch the PySide6 desktop shell."""
    from PySide6.QtWidgets import QApplication

    from frontend.assets import load_app_icon
    from frontend.main_window import MainWindow
    from frontend.theme import APP_STYLESHEET

    application = QApplication([])
    application.setWindowIcon(load_app_icon())
    application.setStyleSheet(APP_STYLESHEET)
    window = MainWindow()
    window.show()
    application.exec()


if __name__ == "__main__":
    main()
