from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openvisionstudio.engine.types import DataType


@dataclass
class PortSpec:
    name: str
    data_type: DataType


@dataclass
class ParamSpec:
    name: str
    param_type: type
    default: Any


class NodeDefinition:
    type_name = "Base.Node"
    display_name = "Base Node"
    inputs: list[PortSpec] = []
    outputs: list[PortSpec] = []
    params: list[ParamSpec] = []

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id

    def compute(
        self, inputs: dict[str, Any], params: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        raise NotImplementedError
