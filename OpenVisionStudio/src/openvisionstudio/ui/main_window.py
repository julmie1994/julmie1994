from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QToolBar,
)

from openvisionstudio import __version__
from openvisionstudio.engine.executor import GraphExecutor
from openvisionstudio.engine.graph_model import ConnectionModel, NodeModel
from openvisionstudio.engine.export_python import export_pipeline_to_python
from openvisionstudio.nodes.builtin import BUILTIN_NODES
from openvisionstudio.plugins import discover_plugin_nodes
from openvisionstudio.ui.console import ConsolePanel
from openvisionstudio.ui.inspector import InspectorPanel
from openvisionstudio.ui.node_canvas import NodeCanvas
from openvisionstudio.ui.node_library import NodeLibrary
from openvisionstudio.ui.preview import ImagePreview


class WorkerSignals(QObject):
    finished = Signal(object)
    progress = Signal(str)


class ExecuteRunnable(QRunnable):
    def __init__(self, executor: GraphExecutor, graph, stop_at: str | None = None):
        super().__init__()
        self.executor = executor
        self.graph = graph
        self.stop_at = stop_at
        self.signals = WorkerSignals()

    def run(self) -> None:
        result = self.executor.execute(
            self.graph,
            context={},
            stop_at_node=self.stop_at,
            progress_cb=self.signals.progress.emit,
        )
        self.signals.finished.emit(result)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OpenVisionStudio")
        self.resize(1400, 900)

        node_types = {cls.type_name: cls for cls in BUILTIN_NODES}
        plugin_dir = Path(__file__).resolve().parents[1] / "plugins"
        for cls in discover_plugin_nodes(plugin_dir):
            node_types[cls.type_name] = cls
        self.node_registry = node_types
        self.executor = GraphExecutor(node_types)
        self.thread_pool = QThreadPool.globalInstance()
        self.current_project: Path | None = None
        self.recent_projects: list[str] = []

        self.node_canvas = NodeCanvas()
        self.setCentralWidget(self.node_canvas)

        self.library = NodeLibrary(list(node_types.keys()))
        self.library.node_requested.connect(self._add_node)
        self.inspector = InspectorPanel()
        self.preview = ImagePreview()
        self.preview.pixel_hovered.connect(self.statusBar().showMessage)
        self.console = ConsolePanel()

        self._build_docks()
        self._build_menu()
        self._build_toolbar()
        self.setStatusBar(QStatusBar())

    def _build_docks(self) -> None:
        left = QDockWidget("Node Library", self)
        left.setWidget(self.library)
        self.addDockWidget(Qt.LeftDockWidgetArea, left)

        right = QDockWidget("Inspector", self)
        right.setWidget(self.inspector)
        self.addDockWidget(Qt.RightDockWidgetArea, right)

        bottom = QDockWidget("Output", self)
        tabs = QTabWidget()
        tabs.addTab(self.preview, "Preview")
        tabs.addTab(self.console, "Console")
        bottom.setWidget(tabs)
        self.addDockWidget(Qt.BottomDockWidgetArea, bottom)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction("New", self.new_project)
        file_menu.addAction("Open", self.open_project)
        file_menu.addAction("Save", self.save_project)
        file_menu.addAction("Save As", self.save_project_as)
        file_menu.addSeparator()
        file_menu.addAction("Export Pipeline to Python", self.export_pipeline)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        run_menu = self.menuBar().addMenu("Run")
        run_menu.addAction("Run All", self.run_all)
        run_menu.addAction("Run to Node", self.run_to_node)

        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction("Reset Layout", lambda: None)

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction("About", self.about)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Run")
        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_all)
        toolbar.addWidget(run_button)
        self.addToolBar(toolbar)

    def _add_node(self, type_name: str) -> None:
        node_id = self.node_canvas.add_node(type_name)
        defaults = {
            p.name: p.default for p in self.node_registry[type_name].params
        }
        self.node_canvas.update_params(node_id, defaults)
        self.console.log(f"Added {type_name} as {node_id}")

    def run_all(self) -> None:
        worker = ExecuteRunnable(self.executor, self.node_canvas.model)
        worker.signals.progress.connect(self.console.log)
        worker.signals.finished.connect(self._on_execution_done)
        self.thread_pool.start(worker)

    def run_to_node(self) -> None:
        if not self.node_canvas.model.nodes:
            return
        node_id = next(reversed(self.node_canvas.model.nodes.keys()))
        worker = ExecuteRunnable(self.executor, self.node_canvas.model, stop_at=node_id)
        worker.signals.progress.connect(self.console.log)
        worker.signals.finished.connect(self._on_execution_done)
        self.thread_pool.start(worker)

    def _on_execution_done(self, result) -> None:
        if result.errors:
            for node_id, error in result.errors.items():
                self.console.log(f"ERROR {node_id}: {error}")
        for node_id in reversed(list(result.outputs.keys())):
            outputs = result.outputs[node_id]
            image = outputs.get("image") or outputs.get("mask")
            if image is not None:
                self.preview.set_image(image)
                break

    def new_project(self) -> None:
        self.node_canvas.model.nodes.clear()
        self.node_canvas.model.connections.clear()
        self.executor.cache.clear()
        self.current_project = None

    def open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "OVS (*.ovs.json)")
        if not path:
            return
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.node_canvas.model.nodes.clear()
        self.node_canvas.model.connections.clear()
        for item in data.get("nodes", []):
            self.node_canvas.model.nodes[item["id"]] = NodeModel(
                node_id=item["id"],
                type_name=item["type"],
                params=item.get("params", {}),
            )
        for c in data.get("connections", []):
            self.node_canvas.model.connections.append(
                ConnectionModel(
                    src_node=c["src_node"],
                    src_port=c["src_port"],
                    dst_node=c["dst_node"],
                    dst_port=c["dst_port"],
                )
            )
        self.current_project = Path(path)

    def _serialize(self) -> dict[str, Any]:
        return {
            "app_version": __version__,
            "schema_version": 1,
            "nodes": [
                {
                    "id": n.node_id,
                    "type": n.type_name,
                    "params": n.params,
                    "position": [0, 0],
                }
                for n in self.node_canvas.model.nodes.values()
            ],
            "connections": [c.__dict__ for c in self.node_canvas.model.connections],
        }

    def save_project(self) -> None:
        if not self.current_project:
            self.save_project_as()
            return
        self.current_project.write_text(json.dumps(self._serialize(), indent=2), encoding="utf-8")

    def save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", "project.ovs.json", "OVS (*.ovs.json)")
        if not path:
            return
        self.current_project = Path(path)
        self.save_project()

    def export_pipeline(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export Pipeline", "pipeline.py", "Python (*.py)")
        if not path:
            return
        Path(path).write_text(export_pipeline_to_python(self.node_canvas.model), encoding="utf-8")
        self.console.log(f"Exported python pipeline to {path}")

    def about(self) -> None:
        QMessageBox.about(
            self,
            "About OpenVisionStudio",
            "OpenVisionStudio is an OSS node-based vision pipeline IDE built with PySide6 and OpenCV.",
        )
