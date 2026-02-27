import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, PortSpec


class DrawOverlayNode(NodeDefinition):
    type_name = "Builtin.DrawOverlay"
    display_name = "Draw Overlay"
    inputs = [PortSpec("image", DataType.IMAGE), PortSpec("contours", DataType.CONTOURS)]
    outputs = [PortSpec("image", DataType.IMAGE)]

    def compute(self, inputs, params, context):
        img = inputs.get("image").copy()
        contours = inputs.get("contours") or []
        cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
        return {"image": img}
