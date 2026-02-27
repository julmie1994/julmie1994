import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, ParamSpec, PortSpec


class ImageLoadNode(NodeDefinition):
    type_name = "Builtin.ImageLoad"
    display_name = "Image Load"
    outputs = [PortSpec("image", DataType.IMAGE)]
    params = [ParamSpec("path", str, "")]

    def compute(self, inputs, params, context):
        path = params.get("path", "")
        if not path:
            raise ValueError("ImageLoad path is empty")
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Failed to read image: {path}")
        return {"image": image}
