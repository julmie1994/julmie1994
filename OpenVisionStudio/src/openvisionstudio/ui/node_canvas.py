from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from openvisionstudio.engine.graph_model import ConnectionModel, GraphModel, NodeModel

try:
    from NodeGraphQt import NodeGraph
except Exception:  # pragma: no cover - fallback for environments without GUI deps
    NodeGraph = None


@dataclass
class CanvasNodeState:
    node_id: str
    type_name: str


class NodeCanvas(QWidget):
    graph_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.model = GraphModel()
        self._counter = 0
        self._ngraph = NodeGraph() if NodeGraph else None
        if self._ngraph:
            self._ngraph.widget.setParent(self)

    def add_node(self, type_name: str) -> str:
        self._counter += 1
        node_id = f"n{self._counter}"
        self.model.nodes[node_id] = NodeModel(node_id=node_id, type_name=type_name)
        self.graph_changed.emit()
        return node_id

    def update_params(self, node_id: str, params: dict) -> None:
        if node_id in self.model.nodes:
            self.model.nodes[node_id].params.update(params)
            self.graph_changed.emit()

    def connect_nodes(self, src_node: str, src_port: str, dst_node: str, dst_port: str) -> None:
        self.model.connections.append(
            ConnectionModel(src_node=src_node, src_port=src_port, dst_node=dst_node, dst_port=dst_port)
        )
        self.graph_changed.emit()
