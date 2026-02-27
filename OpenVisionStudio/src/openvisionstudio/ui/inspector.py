from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QLineEdit, QWidget


class InspectorPanel(QWidget):
    params_changed = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self._layout = QFormLayout(self)
        self._editors: dict[str, QLineEdit] = {}

    def set_params(self, params: dict[str, object]) -> None:
        while self._layout.rowCount():
            self._layout.removeRow(0)
        self._editors.clear()
        for key, value in params.items():
            editor = QLineEdit(str(value))
            editor.editingFinished.connect(self._emit_params)
            self._layout.addRow(key, editor)
            self._editors[key] = editor

    def _emit_params(self) -> None:
        data = {k: v.text() for k, v in self._editors.items()}
        self.params_changed.emit(data)
