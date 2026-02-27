import sys

from PySide6.QtWidgets import QApplication

from openvisionstudio.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("OpenVisionStudio")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
