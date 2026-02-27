import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, ParamSpec, PortSpec


class MorphologyNode(NodeDefinition):
    type_name = "Builtin.Morphology"
    display_name = "Morphology"
    inputs = [PortSpec("mask", DataType.MASK)]
    outputs = [PortSpec("mask", DataType.MASK)]
    params = [ParamSpec("op", str, "open"), ParamSpec("ksize", int, 3)]

    OPS = {
        "erode": cv2.MORPH_ERODE,
        "dilate": cv2.MORPH_DILATE,
        "open": cv2.MORPH_OPEN,
        "close": cv2.MORPH_CLOSE,
    }

    def compute(self, inputs, params, context):
        img = inputs.get("mask")
        ksize = int(params.get("ksize", 3))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksize, ksize))
        op = self.OPS[params.get("op", "open")]
        return {"mask": cv2.morphologyEx(img, op, kernel)}
