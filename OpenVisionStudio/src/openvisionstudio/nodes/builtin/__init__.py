from openvisionstudio.nodes.builtin.blur import BlurNode
from openvisionstudio.nodes.builtin.canny import CannyNode
from openvisionstudio.nodes.builtin.connected_components import ConnectedComponentsNode
from openvisionstudio.nodes.builtin.contours import FindContoursNode
from openvisionstudio.nodes.builtin.convert_color import ConvertColorNode
from openvisionstudio.nodes.builtin.draw_overlay import DrawOverlayNode
from openvisionstudio.nodes.builtin.image_load import ImageLoadNode
from openvisionstudio.nodes.builtin.morphology import MorphologyNode
from openvisionstudio.nodes.builtin.resize import ResizeNode
from openvisionstudio.nodes.builtin.save_image import SaveImageNode
from openvisionstudio.nodes.builtin.threshold import ThresholdNode
from openvisionstudio.nodes.builtin.video_capture import VideoCaptureNode

BUILTIN_NODES = [
    ImageLoadNode,
    VideoCaptureNode,
    ResizeNode,
    ConvertColorNode,
    BlurNode,
    ThresholdNode,
    MorphologyNode,
    CannyNode,
    FindContoursNode,
    ConnectedComponentsNode,
    DrawOverlayNode,
    SaveImageNode,
]
