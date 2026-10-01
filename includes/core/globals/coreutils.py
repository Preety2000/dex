import os
import re
import uuid
import base64
import unicodedata
from io import BytesIO
from PIL import Image
from datetime import datetime
from typing import Any,  List, Union, Optional

from fastapi.responses import StreamingResponse
from includes.core.repo.dir_manager import folder


def is_empty(value: Any) -> bool:
    """Checks if a string, list, dict, or collection is empty."""
    if isinstance(value, (int, float)):
        return False
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    if isinstance(value, str):
        return len(value.strip()) == 0
    return not bool(value)


def deep_replace(data: Any, replacements: Optional[dict[Any, Any]] = None) -> Any:
    """Recursively replaces values/keys in nested structures (dicts, lists, tuples, strings)."""
    if replacements is None:
        replacements = {False: 0, True: 1, None: ""}
    if isinstance(data, dict):
        return {
            deep_replace(k, replacements): deep_replace(v, replacements)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [deep_replace(item, replacements) for item in data]
    elif isinstance(data, tuple):
        return tuple(deep_replace(item, replacements) for item in data)
    for key, val in replacements.items():
        if type(data) is type(key) and data == key:
            return val
    if isinstance(data, str):
        for old, new in replacements.items():
            data = data.replace(str(old), str(new))
        return data
    return data


def generate_unique_uuid(existing_ids: Optional[List[str]] = None) -> str:
    """Generates a UUID4 that does not exist in the provided list."""
    existing_set = set(existing_ids) if existing_ids else set()
    while True:
        new_uuid = str(uuid.uuid4())
        if new_uuid not in existing_set:
            return new_uuid


def encode_id(number: int, salt: int = 25071998) -> str:
    """Encodes an integer ID into a URL-safe Base64 hash string."""
    salted = number + salt
    byte_len = (salted.bit_length() + 7) // 8
    number_bytes = salted.to_bytes(max(1, byte_len), byteorder="big")
    return base64.urlsafe_b64encode(number_bytes).decode("utf-8").rstrip("=")


def decode_id(encoded_str: str, salt: int = 25071998) -> int:
    """Decodes a URL-safe Base64 string back into the original integer ID."""
    padding = "=" * ((4 - len(encoded_str) % 4) % 4)
    padded_str = encoded_str + padding
    number_bytes = base64.urlsafe_b64decode(padded_str)
    return int.from_bytes(number_bytes, byteorder="big") - salt


def slugify(text: str) -> str:
    """Converts text into a clean, URL-friendly slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def format_datetime(
    dt_input: Union[int, float, str, datetime], fmt: str = "%d %B, %Y at %H:%M"
) -> str:
    """Formats an ISO string, epoch integer, or datetime object into a clean string."""
    if isinstance(dt_input, (int, float)):
        dt = datetime.fromtimestamp(dt_input)
    elif isinstance(dt_input, str):
        dt = datetime.fromisoformat(dt_input)
    elif isinstance(dt_input, datetime):
        dt = dt_input
    else:
        raise ValueError("Unsupported datetime input type.")
    return dt.strftime(fmt)


def format_view_count(num: Union[int, float, str]) -> str:
    """Formats large numbers into human-readable compact strings (e.g., 1.5k, 2M)."""
    if not num:
        return "0"
    value = float(num)
    suffixes = ["", "k", "m", "b", "t"]
    magnitude = 0
    while abs(value) >= 1000 and magnitude < len(suffixes) - 1:
        value /= 1000.0
        magnitude += 1
    formatted = f"{value:.1f}".rstrip("0").rstrip(".")
    return f"{formatted}{suffixes[magnitude]}"


def process_image(
    image_relative_path: str,
    output_type: str = "base64",
    *,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Union[dict[str, Any], StreamingResponse, str]:
    """
    Processes an image (resizing, converting to WebP) and returns Base64 or StreamingResponse.
    """

    image_path = os.path.join(folder.static_folder, image_relative_path)
    if not os.path.exists(image_path):
        return "Image unavailable."
    try:
        with Image.open(image_path) as base_image:
            if width and height:
                base_image = base_image.resize((width, height))
            orig_width, orig_height = base_image.size
            image_io = BytesIO()
            base_image.save(image_io, format="WEBP")
            image_bytes = image_io.getvalue()
            if output_type in ("img", "ico"):
                media_type = "image/x-icon" if output_type == "ico" else "image/webp"
                return StreamingResponse(BytesIO(image_bytes), media_type=media_type)
            base64_str = base64.b64encode(image_bytes).decode("utf-8")
            base64_header = f"data:image/webp;base64,{base64_str}"
            return {
                "width": orig_width,
                "height": orig_height,
                "type": "image/webp",
                "image": base64_header,
            }
    except Exception as e:
        return f"Error processing image: {str(e)}"


def get_active_class(current_state: str, target_state: str) -> str:
    """Returns 'active' or 'deactive' CSS classes based on equality match."""
    return "active" if current_state == target_state else "deactive"


def error_response(message: str, error_code: str = "Ex00005") -> List[Any]:
    """Returns a unified error tuple for API handling."""
    return [None, {"status": "error", "message": message, "error_code": error_code}]


def matches_filters(record: Any, filters: dict[str, Any]) -> bool:
    for k, v in filters.items():
        if v is not None and getattr(record, k, None) != v:
            return False
    return True