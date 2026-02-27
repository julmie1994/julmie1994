import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, ParamSpec, PortSpec


class VideoCaptureNode(NodeDefinition):
    type_name = "Builtin.VideoCapture"
    display_name = "Video Capture"
    outputs = [PortSpec("image", DataType.IMAGE)]
    params = [ParamSpec("index", int, 0)]

    def compute(self, inputs, params, context):
        idx = int(params.get("index", 0))
        key = f"cap:{idx}"
        cap = context.get(key)
        if cap is None:
            cap = cv2.VideoCapture(idx)
            context[key] = cap
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError("Could not read frame from webcam")
        return {"image": frame}
