from dataclasses import dataclass
import os
import re
import json
import time
from types import SimpleNamespace
import uuid
import random
import string
import base64
import unicodedata
from io import BytesIO
from urllib.parse import parse_qs
from datetime import datetime
from urllib.parse import parse_qs, urlencode
from fastapi.responses import StreamingResponse
from sqlalchemy import asc, desc

# from includes.config import self.state
# from includes.schemas.captcha import Captcha
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from includes.core.security import _Security

# Example of using a global variable (not recommended for FastAPI)
# This is a global configuration object or variable


@dataclass
class FilterData:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    asc: str = None
    desc: str = None
    search: str = None
    olderThan: dict = dict


session_creator_manager = {"version": "1.0.0", "app_name": "MyFastAPIApp"}


def get_unique_id() -> str:
    """8-char ID using time + randomness."""
    value = time.time_ns() ^ random.getrandbits(32)
    return _Security.short_encode(value)[-8:]


# You can also store configurations or any shared data here
async def get_global(key=None):
    # return  session_creator_manager
    return (
        await session_creator_manager.get(key) if key else await session_creator_manager
    )


def set_global(key, value):
    session_creator_manager[key] = value


async def load_svg_files(self):
    svg_files = {}

    for file in os.listdir(self.folder.static_svg):
        if file.endswith(".svg"):
            path = os.path.join(self.folder.static_svg, file)

            with open(path, "r", encoding="utf-8") as f:
                svg_files[file.replace(".svg", "")] = f.read()

    return svg_files


class Functions:
    def __init__(self, state):
        self.state = state
        pass

    def is_post(self):
        return self.state.request.method == "POST"

    def is_api(self):
        return self.state.request.method == "POST" and self.get_request_value("key")

    def get_next_id(self, table):
        query = (
            getattr(self.state.session, table.__tablename__).order_by(table.id).all()
        )
        for index, item in enumerate(query, start=0):
            if item.id != index:
                return index

        return len(query) + 1

    def get_request_value(self, value, default=None):
        return self.state.request.query_params.get(value, default)

    def getRequestInt(self, value, default=None):
        value = self.get_request_value(value, default)
        try:
            value = int(value)
        except:
            pass
        return value if isinstance(value, (int, float)) else default

    def utc(self, string):
        lowerString = re.sub(r"\s+", "", string.lower())
        lowerString = self.state.request.state.menuname.get(lowerString)
        return lowerString or string

    def active_class(self, type, action):
        return "active" if type == action else "deactive"

    def resize_and_compress_image(self, image, target_size=10):
        buffer = BytesIO()
        best_buffer = None
        best_size = float("inf")
        target_bytes = self.getRequestInt("st", (target_size * 1024))

        if format in ("JPEG", "JPG") and image.mode != "RGB":
            image = image.convert("RGB")

        if dimensions := self.getRequestInt("si"):
            max_dimensions = (dimensions, dimensions)
            image.thumbnail(max_dimensions, Image.Resampling.LANCZOS)

        for quality in range(100, 1, -5):
            buffer.seek(0)
            buffer.truncate()
            image.save(buffer, format="JPEG", quality=quality, optimize=True)
            size = buffer.tell()

            if size <= target_bytes:
                buffer.seek(0)
                return buffer

            if size < best_size:
                best_size = size
                best_buffer = BytesIO(buffer.getvalue())

        return best_buffer if best_buffer else None
