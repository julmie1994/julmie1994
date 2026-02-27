import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, PortSpec


class FindContoursNode(NodeDefinition):
    type_name = "Builtin.FindContours"
    display_name = "Find Contours"
    inputs = [PortSpec("mask", DataType.MASK)]
    outputs = [PortSpec("contours", DataType.CONTOURS), PortSpec("stats", DataType.TABLE)]

    def compute(self, inputs, params, context):
        mask = inputs.get("mask")
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        stats = [{"area": float(cv2.contourArea(c))} for c in contours]
        return {"contours": contours, "stats": stats}
