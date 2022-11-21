from typing import Protocol
import numpy as np
from abc import abstractmethod
from typing import Optional


class SegmentationBackend(Protocol):
    @abstractmethod
    def submit_roi(self, id, roi: np.ndarray) -> bool:
        """
        Submit an roi for the given image id to the backend.
        this method should return True if the submission was successful,
        or return False and print an error message to the console if it
        is unsuccessful
        """

    @abstractmethod
    def get_path_to_image(self, id) -> str:
        """
        Returns a path to the image with the specified id.
        """

    @abstractmethod
    def get_info_for_image(self, id) -> dict:
        """
        Returns any additional info necessary for the specified image id.
        For example:
            {'saved': true}
        """

    @abstractmethod
    def list_all_ids(self) -> list[str]:
        """
        Return a list of all the image IDs that will be segmented
        """

    @abstractmethod
    def setup(self) -> None:
        """
        Anything that needs to be done when first starting the app
        (e.g downloading all the necessary files, setting up the
        file structure to run the app, etc) should be done here
        """

    @abstractmethod
    def finish(self) -> None:
        """
        Anything that needs to be done when finished with running the
        app (for example, push the saved ROIs from a local file system
        to a server, any cleanup necessary) should be done here
        """
