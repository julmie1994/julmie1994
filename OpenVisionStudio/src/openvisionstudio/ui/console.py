from PySide6.QtWidgets import QPlainTextEdit


class ConsolePanel(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)

    def log(self, message: str) -> None:
        self.appendPlainText(message)
