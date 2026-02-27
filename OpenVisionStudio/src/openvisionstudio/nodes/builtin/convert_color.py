import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, ParamSpec, PortSpec


class ConvertColorNode(NodeDefinition):
    type_name = "Builtin.ConvertColor"
    display_name = "Convert Color"
    inputs = [PortSpec("image", DataType.IMAGE)]
    outputs = [PortSpec("image", DataType.IMAGE)]
    params = [ParamSpec("mode", str, "BGR2GRAY")]

    MODES = {
        "BGR2GRAY": cv2.COLOR_BGR2GRAY,
        "GRAY2BGR": cv2.COLOR_GRAY2BGR,
        "BGR2HSV": cv2.COLOR_BGR2HSV,
        "HSV2BGR": cv2.COLOR_HSV2BGR,
    }

    def compute(self, inputs, params, context):
        img = inputs.get("image")
        mode = params.get("mode", "BGR2GRAY")
        return {"image": cv2.cvtColor(img, self.MODES[mode])}
