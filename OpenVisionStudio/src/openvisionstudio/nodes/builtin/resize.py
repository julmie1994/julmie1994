import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, ParamSpec, PortSpec


class ResizeNode(NodeDefinition):
    type_name = "Builtin.Resize"
    display_name = "Resize"
    inputs = [PortSpec("image", DataType.IMAGE)]
    outputs = [PortSpec("image", DataType.IMAGE)]
    params = [ParamSpec("width", int, 640), ParamSpec("height", int, 480)]

    def compute(self, inputs, params, context):
        img = inputs.get("image")
        if img is None:
            raise ValueError("Resize requires image input")
        out = cv2.resize(img, (int(params.get("width", 640)), int(params.get("height", 480))))
        return {"image": out}
