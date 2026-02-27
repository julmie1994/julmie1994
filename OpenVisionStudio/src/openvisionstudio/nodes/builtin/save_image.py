import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, ParamSpec, PortSpec


class SaveImageNode(NodeDefinition):
    type_name = "Builtin.SaveImage"
    display_name = "Save Image"
    inputs = [PortSpec("image", DataType.IMAGE)]
    outputs = [PortSpec("path", DataType.SCALAR)]
    params = [ParamSpec("path", str, "output.png")]

    def compute(self, inputs, params, context):
        img = inputs.get("image")
        path = params.get("path", "output.png")
        if not cv2.imwrite(path, img):
            raise RuntimeError(f"Failed to save image at {path}")
        return {"path": path}
