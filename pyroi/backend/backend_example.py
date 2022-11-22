from .backend_base import SegmentationBackend
import os
import skimage.data as skimage_data
import numpy as np
from PIL import Image


class DummySegmentations(SegmentationBackend):
    def __init__(self, work_dir):

        self.work_dir = work_dir

        if not os.path.isdir(self.work_dir):
            try:
                os.mkdir(self.work_dir)
            except:
                raise ValueError(
                    f"Directory {self.work_dir} does not exist and could not be created."
                )

        self.index = 0
        self.data = ["cat", "hubble_deep_field", "astronaut", "camera"]
        self.data.sort()

    def setup(self) -> None:
        for item in self.data:
            image = getattr(skimage_data, item)()
            path = os.path.join(self.work_dir, f"{item}_image.png")
            Image.fromarray(image).save(path)

        return super().setup()

    def list_all_ids(self) -> list[str]:
        return self.data

    def get_info_for_image(self, id):
        if f"{id}_roi.png" in os.listdir(self.work_dir):
            return {"saved": True}
        else:
            return {}

    def get_path_to_image(self, id) -> str:
        return os.path.join(self.work_dir, f"{id}_image.png")

    def submit_roi(self, id, roi: np.ndarray) -> bool:

        fpath = os.path.join(self.work_dir, f"{id}_roi.png")
        from PIL import Image

        im = Image.fromarray(roi.astype("bool"))
        im.save(fpath)

        return True

    def finish(self):
        print("Segmentations Finished!")
