from pyroi.segmentation_server import SegmentationServer
from pyroi.backend.backend_example import DummySegmentations

app = SegmentationServer(DummySegmentations("example")).app
