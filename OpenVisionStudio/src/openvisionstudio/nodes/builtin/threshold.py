import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, ParamSpec, PortSpec


class ThresholdNode(NodeDefinition):
    type_name = "Builtin.Threshold"
    display_name = "Threshold"
    inputs = [PortSpec("image", DataType.IMAGE)]
    outputs = [PortSpec("mask", DataType.MASK)]
    params = [ParamSpec("value", int, 127)]

    def compute(self, inputs, params, context):
        img = inputs.get("image")
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(img, int(params.get("value", 127)), 255, cv2.THRESH_BINARY)
        return {"mask": mask}
