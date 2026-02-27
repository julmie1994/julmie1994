import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, ParamSpec, PortSpec


class CannyNode(NodeDefinition):
    type_name = "Builtin.Canny"
    display_name = "Canny"
    inputs = [PortSpec("image", DataType.IMAGE)]
    outputs = [PortSpec("mask", DataType.MASK)]
    params = [ParamSpec("low", int, 50), ParamSpec("high", int, 150)]

    def compute(self, inputs, params, context):
        img = inputs.get("image")
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = cv2.Canny(img, int(params.get("low", 50)), int(params.get("high", 150)))
        return {"mask": mask}
