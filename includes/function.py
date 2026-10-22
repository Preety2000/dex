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
from includes.core.repo.dir_manager import folder
from includes.utils.utils import get_post_value

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


async def load_svg_files():
    svg_files = {}

    for file in os.listdir(folder.static_svg):
        if file.endswith(".svg"):
            path = os.path.join(folder.static_svg, file)

            with open(path, "r", encoding="utf-8") as f:
                svg_files[file.replace(".svg", "")] = f.read()

    return svg_files


class Functions:
    def __init__(self, state):
        self.state = state
        pass

    def utc(self, string):
        return string

    def active_class(self, type, action):
        return "active" if type == action else "deactive"
