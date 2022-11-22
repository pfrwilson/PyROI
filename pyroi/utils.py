import binascii
from PIL import Image
import binascii
from io import BytesIO
import numpy as np


def data_url_to_pil(url: str):
    roi_data = url
    if not roi_data.startswith("data:image/png;base64,"):
        raise ValueError(
            "Attempting to parse data url, but data string does not appear to be a data url."
        )
    roi_data = roi_data.removeprefix("data:image/png;base64,")
    bin = binascii.a2b_base64(roi_data)
    image = Image.open(BytesIO(bin))
    return image


def rgba_image_to_binary_mask(image):
    return np.array(image.convert("LA"))[..., 1] != 0


def save_binary_mask(mask: np.ndarray, fpath):
    Image.fromarray(mask).save(fpath)
