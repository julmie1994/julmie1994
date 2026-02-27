import cv2

from openvisionstudio.engine.types import DataType
from openvisionstudio.nodes.base import NodeDefinition, PortSpec


class ConnectedComponentsNode(NodeDefinition):
    type_name = "Builtin.ConnectedComponents"
    display_name = "Connected Components"
    inputs = [PortSpec("mask", DataType.MASK)]
    outputs = [PortSpec("labels", DataType.IMAGE), PortSpec("stats", DataType.TABLE)]

    def compute(self, inputs, params, context):
        mask = inputs.get("mask")
        count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        rows = []
        for idx in range(1, count):
            rows.append(
                {
                    "label": idx,
                    "x": int(stats[idx, cv2.CC_STAT_LEFT]),
                    "y": int(stats[idx, cv2.CC_STAT_TOP]),
                    "w": int(stats[idx, cv2.CC_STAT_WIDTH]),
                    "h": int(stats[idx, cv2.CC_STAT_HEIGHT]),
                    "area": int(stats[idx, cv2.CC_STAT_AREA]),
                }
            )
        return {"labels": labels, "stats": rows}
