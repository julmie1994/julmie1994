import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, ParamSpec, PortSpec


class BlurNode(NodeDefinition):
    type_name = "Builtin.Blur"
    display_name = "Gaussian Blur"
    inputs = [PortSpec("image", DataType.IMAGE)]
    outputs = [PortSpec("image", DataType.IMAGE)]
    params = [ParamSpec("ksize", int, 5)]

    def compute(self, inputs, params, context):
        img = inputs.get("image")
        ksize = int(params.get("ksize", 5))
        if ksize % 2 == 0:
            ksize += 1
        return {"image": cv2.GaussianBlur(img, (ksize, ksize), 0)}
