from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable

from openvisionstudio.engine.cache import NodeCache
from openvisionstudio.engine.graph_model import GraphModel
from openvisionstudio.nodes.base import NodeDefinition


@dataclass
class ExecutionResult:
    outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)


class GraphExecutor:
    def __init__(self, node_registry: dict[str, type[NodeDefinition]]) -> None:
        self.node_registry = node_registry
        self.cache = NodeCache()

    def _signature(self, node_id: str, params: dict[str, Any], upstream_sigs: list[str]) -> str:
        data = {
            "node_id": node_id,
            "params": params,
            "upstream": upstream_sigs,
        }
        payload = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def execute(
        self,
        graph: GraphModel,
        context: dict[str, Any] | None = None,
        stop_at_node: str | None = None,
        progress_cb: Callable[[str], None] | None = None,
    ) -> ExecutionResult:
        if context is None:
            context = {}
        result = ExecutionResult()
        signatures: dict[str, str] = {}

        order = graph.topological_sort()
        for node_id in order:
            node_model = graph.nodes[node_id]
            node_cls = self.node_registry[node_model.type_name]
            node = node_cls(node_id=node_id)

            input_values: dict[str, Any] = {}
            upstream_sigs = []
            for conn in graph.upstream(node_id):
                output_map = result.outputs.get(conn.src_node, {})
                input_values[conn.dst_port] = output_map.get(conn.src_port)
                upstream_sigs.append(signatures.get(conn.src_node, ""))

            sig = self._signature(node_id, node_model.params, upstream_sigs)
            signatures[node_id] = sig
            cached = self.cache.get(node_id, sig)
            if cached is not None:
                result.outputs[node_id] = cached
                if progress_cb:
                    progress_cb(f"{node_id}: cache hit")
                if stop_at_node == node_id:
                    break
                continue

            try:
                outputs = node.compute(input_values, node_model.params, context)
                result.outputs[node_id] = outputs
                self.cache.put(node_id, sig, outputs)
                if progress_cb:
                    progress_cb(f"{node_id}: executed")
            except Exception as exc:
                result.errors[node_id] = str(exc)
                result.outputs[node_id] = {}
                if progress_cb:
                    progress_cb(f"{node_id}: error {exc}")

            if stop_at_node == node_id:
                break

        return result
