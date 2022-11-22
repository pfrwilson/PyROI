from asyncio import sleep, gather
import binascii
import json
from time import time
from PIL import Image
from typing import Optional
from fastapi import Request
from fastapi import FastAPI
from fastapi import Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    JSONResponse,
    RedirectResponse,
    Response,
)
from fastapi.templating import Jinja2Templates
import os
import shutil
from pydantic import BaseModel
import urllib
from . import utils
from io import BytesIO
from .backend.backend_base import SegmentationBackend
import pkg_resources


class SegmentationServer:
    def __init__(self, backend: SegmentationBackend):

        backend.setup()

        self.all_rois = backend.list_all_ids()
        self.rois_are_saved = []
        for roi in self.all_rois:
            if backend.get_info_for_image(roi).get("saved"):
                self.rois_are_saved.append(True)
            else:
                self.rois_are_saved.append(False)

        self.current_seg_idx = None
        self.seg2idx = {roi: idx for idx, roi in enumerate(self.all_rois)}
        self._welcome_shown = False

        app = FastAPI()
        app.mount(
            "/static",
            StaticFiles(directory=pkg_resources.resource_filename(__name__, "static")),
        )
        templates = Jinja2Templates(
            pkg_resources.resource_filename(__name__, "templates")
        )

        @app.get("/favicon.ico")
        async def favicon():
            return RedirectResponse("/static/favicon.ico")

        @app.get("/")
        async def root(request: Request):
            if not self._welcome_shown:
                return RedirectResponse(app.url_path_for("welcome"))

            roi_infos = zip(self.all_rois, self.rois_are_saved)
            total_rois = len(self.all_rois)
            saved_rois = sum(self.rois_are_saved)
            return templates.TemplateResponse(
                "navigation.html",
                {
                    "request": request,
                    "roi_infos": roi_infos,
                    "total_rois": total_rois,
                    "saved_rois": saved_rois,
                },
            )

        @app.get("/welcome")
        async def welcome(request: Request):
            self._welcome_shown = True
            return templates.TemplateResponse(
                "welcome.html",
                {"request": request, "backend_name": str(backend.__class__.__name__)},
            )

        @app.get("/images/{image_id}")
        async def get_image(image_id: str):
            path = backend.get_path_to_image(image_id)
            return FileResponse(path)

        @app.get("/segmentation/{image_id}")
        async def segmentation_app(request: Request, image_id):
            self.current_seg_idx = self.seg2idx[image_id]
            data = {"image_id": image_id}

            return templates.TemplateResponse(
                "roi_app.html",
                {
                    "request": request,
                    "image_id": image_id,
                    "saved": self.rois_are_saved[self.current_seg_idx],
                    "data": json.dumps(data),
                    "current_idx": self.current_seg_idx + 1,
                    "total": len(self.all_rois),
                },
            )

        @app.get("/next")
        async def next():
            next_idx = self.current_seg_idx + 1

            if next_idx >= len(self.all_rois):
                self.current_seg_idx = None
                return RedirectResponse(app.url_path_for("root"))

            next_roi = self.all_rois[self.current_seg_idx + 1]

            return RedirectResponse(
                app.url_path_for("segmentation_app", image_id=next_roi)
            )

        @app.get("/back")
        async def back():
            next_idx = self.current_seg_idx - 1

            if next_idx < 0:
                self.current_seg_idx = None
                return RedirectResponse(app.url_path_for("root"))

            next_roi = self.all_rois[next_idx]

            return RedirectResponse(
                app.url_path_for("segmentation_app", image_id=next_roi)
            )

        class ROISubmission(BaseModel):
            id: str
            roi: str

        @app.post("/submit_roi")
        async def process_roi(roi: ROISubmission):

            try:
                image = utils.data_url_to_pil(roi.roi)
                mask = utils.rgba_image_to_binary_mask(image)
                # utils.save_binary_mask(mask, "mask.png")
                import matplotlib.pyplot as plt

                success = backend.submit_roi(roi.id, mask)

                if success:
                    self.rois_are_saved[self.current_seg_idx] = True
                return {"success": success}

            except:
                return {"success": False}

        @app.get("/finish")
        async def finish():
            backend.finish()
            return RedirectResponse(app.url_path_for("welcome"))

        self.app = app
