from dataclasses import dataclass
from PIL import Image

from includes.utils.utils import get_query_value


@dataclass
class ImageCropBounds:
    """Cropping coordinates ko hold aur validate karta hai."""

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    @classmethod
    def from_request_query(cls):
        """Query parameters se safely parse karta hai."""
        return cls(
            x=float(get_query_value("positionx") or 0),
            y=float(get_query_value("positiony") or 0),
            width=float(get_query_value("width") or 0),
            height=float(get_query_value("height") or 0),
        )


class ImageProcessor:
    """Image manipulation aur metadata injection ke liye primary processor class."""

    @staticmethod
    def apply_crop(
        image: Image.Image, bounds: ImageCropBounds | None = None
    ) -> tuple[bool, Image.Image]:
        crop_bounds = bounds or ImageCropBounds.from_request_query()
        img_width, img_height = image.size

        if crop_bounds.width <= 0 or crop_bounds.height <= 0:
            return False, image

        left = max(0, round(crop_bounds.x))
        top = max(0, round(crop_bounds.y))
        right = min(img_width, round(crop_bounds.x + crop_bounds.width))
        bottom = min(img_height, round(crop_bounds.y + crop_bounds.height))

        if left >= right or top >= bottom:
            return False, image

        return True, image.crop((left, top, right, bottom))

    @staticmethod
    def build_exif_metadata(
        image: Image.Image, metadata: dict | None = None
    ) -> Image.Exif:
        exif = image.getexif()
        user_meta = metadata or {}

        # Camera info
        camera = user_meta.get("camera", {})
        if camera.get("make"):
            exif[271] = camera["make"]
        if camera.get("model"):
            exif[272] = camera["model"]
        if camera.get("lens"):
            exif[42036] = camera["lens"]

        # Date & Time
        if user_meta.get("datetime"):
            exif[36867] = user_meta["datetime"]
            exif[36868] = user_meta["datetime"]

        # General tags
        if user_meta.get("orientation"):
            exif[274] = user_meta["orientation"]
        if user_meta.get("artist"):
            exif[315] = user_meta["artist"]
        if user_meta.get("description"):
            exif[270] = user_meta["description"]

        # Software & Copyright defaults
        exif[305] = user_meta.get("software", "MyApplication 2.054.SH")
        exif[33432] = user_meta.get(
            "copyright", "Copyright © 2026. All rights reserved."
        )

        return exif
