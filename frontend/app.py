"""Desktop application entry point."""

from __future__ import annotations


def main() -> None:
    """Launch the PySide6 desktop shell."""
    from PySide6.QtWidgets import QApplication

    from frontend.main_window import MainWindow

    application = QApplication([])
    window = MainWindow()
    window.show()
    application.exec()


if __name__ == "__main__":
    main()
