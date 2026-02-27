from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class NodeLibrary(QWidget):
    node_requested = Signal(str)

    def __init__(self, node_types: list[str]) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        for node_type in sorted(node_types):
            QListWidgetItem(node_type, self.list_widget)
        self.list_widget.itemDoubleClicked.connect(self._on_double_clicked)
        layout.addWidget(self.list_widget)

    def _on_double_clicked(self, item):
        self.node_requested.emit(item.text())
