from roi_boy.segmentation_server import SegmentationServer
from roi_boy.backend.backend_example import DummySegmentations

app = SegmentationServer(DummySegmentations("example")).app
