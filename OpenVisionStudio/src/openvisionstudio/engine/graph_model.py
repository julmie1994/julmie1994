from dataclasses import dataclass, field
from typing import Any


@dataclass
class NodeModel:
    node_id: str
    type_name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectionModel:
    src_node: str
    src_port: str
    dst_node: str
    dst_port: str


@dataclass
class GraphModel:
    nodes: dict[str, NodeModel] = field(default_factory=dict)
    connections: list[ConnectionModel] = field(default_factory=list)

    def upstream(self, node_id: str) -> list[ConnectionModel]:
        return [c for c in self.connections if c.dst_node == node_id]

    def downstream(self, node_id: str) -> list[ConnectionModel]:
        return [c for c in self.connections if c.src_node == node_id]

    def topological_sort(self) -> list[str]:
        indegree = {node_id: 0 for node_id in self.nodes}
        for c in self.connections:
            indegree[c.dst_node] += 1

        queue = [node_id for node_id, d in indegree.items() if d == 0]
        ordered: list[str] = []

        while queue:
            node_id = queue.pop(0)
            ordered.append(node_id)
            for c in self.downstream(node_id):
                indegree[c.dst_node] -= 1
                if indegree[c.dst_node] == 0:
                    queue.append(c.dst_node)

        if len(ordered) != len(self.nodes):
            raise ValueError("Cycle detected in graph.")
        return ordered
