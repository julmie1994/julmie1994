from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Iterable

from openvisionstudio.nodes.base import NodeDefinition


def discover_plugin_nodes(plugin_dir: Path) -> list[type[NodeDefinition]]:
    nodes: list[type[NodeDefinition]] = []
    if not plugin_dir.exists():
        return nodes

    for path in plugin_dir.glob("*.py"):
        if path.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if not spec or not spec.loader:
            continue
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        plugin_nodes: Iterable[type[NodeDefinition]] = getattr(mod, "PLUGIN_NODES", [])
        nodes.extend(plugin_nodes)
    return nodes
