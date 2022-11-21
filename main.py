from roiboy.segmentation_server import SegmentationServer
from roiboy.backend.backend_example import DummySegmentations

app = SegmentationServer(DummySegmentations("example")).app
