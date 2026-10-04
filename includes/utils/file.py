import copy
import json
import os
import subprocess
import time
import cv2
import platform
from typing import List,  Any, Optional

# pip install opencv-python
from dataclasses import dataclass

import exiftool
from fastapi import UploadFile
import numpy as np

from includes.core.globals.entry import app_context
from includes.database.chait.media_asset_model import MediaAsset
from includes.utils.utils import get_query_value, json_null_response, json_response


from io import BytesIO
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

# Dictionary to map MIME types to category
MIME_TYPES = {
    "image": [
        "image/jpeg",  # JPEG image
        "image/png",  # PNG image
        "image/gif",  # GIF image
        "image/bmp",  # BMP image
        "image/tiff",  # TIFF image
        "image/svg+xml",  # SVG image
        "image/webp",  # WebP image
        "image/ico",  # ICO image
        "image/heif",  # HEIF image
        "image/heic",  # HEIC image
    ],
    "video": [
        "video/mp4",  # MPEG-4 Video
        "video/webm",  # WebM Video
        "video/ogg",  # Ogg Video
        "video/avi",  # Audio Video Interleave
        "video/mpeg",  # MPEG Video
        "video/quicktime",  # QuickTime Video
        "video/x-msvideo",  # Microsoft Video
        "video/x-ms-wmv",  # Windows Media Video
        "video/x-flv",  # Flash Video
        "video/3gpp",  # 3GPP Video
        "video/3gpp2",  # 3GPP2 Video
        "video/x-matroska",  # Matroska Video
        "video/x-m4v",  # M4V Video
    ],
    "audio": [
        "audio/mpeg",  # MP3 audio
        "audio/wav",  # WAV audio
        "audio/ogg",  # Ogg Vorbis audio
        "audio/aac",  # AAC audio
        "audio/flac",  # FLAC audio
        "audio/midi",  # MIDI audio
        "audio/x-m4a",  # M4A audio
        "audio/webm",  # WebM audio
        "audio/opus",  # Opus audio
        "audio/3gpp",  # 3GPP audio
        "audio/3gpp2",  # 3GPP2 audio
        "audio/pcm",  # PCM audio
        "audio/x-ms-wma",  # Windows Media Audio
        "audio/ts",  # MPEG-TS audio
    ],
    "pdf": [
        "application/pdf",  # Standard PDF format
        "application/x-pdf",  # Alternative name for PDF
        "application/acrobat",  # Old MIME type for PDF
        "application/vnd.pdf",  # Vendor-specific type, rarely used
    ],
}

colors = {
    "A": "#7A1F1B",
    "B": "#740F32",
    "C": "#4E1458",
    "D": "#341D5C",
    "E": "#1F285A",
    "F": "#104C7A",
    "G": "#027D7A",
    "H": "#005E6A",
    "I": "#004C44",
    "J": "#266226",
    "K": "#46621E",
    "L": "#666E1C",
    "M": "#806004",
    "N": "#7C4C00",
    "O": "#7A2B11",
    "P": "#3C2A24",
    "Q": "#303E44",
    "R": "#78304A",
    "S": "#5D3464",
    "T": "#3C4064",
    "U": "#325A7A",
    "V": "#026A70",
    "W": "#265A56",
    "X": "#40623C",
    "Y": "#6E703C",
    "Z": "#6A3A2A",
}


async def get_files(*, name=None, ALLOWED_EXTENSIONS=[]):

    uploaded_files = await app_context.request.form()

    def allowed_file(filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
            if ALLOWED_EXTENSIONS
            else True
        )

    FILES = {}
    for field_name, file in uploaded_files.items():
        if isinstance(file, UploadFile) and allowed_file(file.filename):
            file_content = await file.read()
            file.size = len(file_content)
            file.seek(0)

        FILES[field_name] = file

    return FILES.get(name) if name else FILES


async def looks_like_signature(file: UploadFile) -> bool:
    file = copy.deepcopy(file)

    file_bytes = await file.read()

    if not file_bytes:
        return False

    img_array = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

    if img is None:
        return False

    # Very small images reject
    height, width = img.shape

    if width < 100 or height < 30:
        return False

    # Threshold dark pixels
    _, binary = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY_INV)

    # Kitne pixels dark/ink hain
    ink_pixels = cv2.countNonZero(binary)
    total_pixels = width * height

    ink_ratio = ink_pixels / total_pixels

    print("ink_pixels", ink_pixels)
    print("total_pixels", total_pixels, ink_ratio)
    # Completely blank image
    if ink_ratio < 0.005:
        return False

    # Almost completely dark image
    # if ink_ratio > 0.40:
    #     return False

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return False

    # Remove tiny noise
    significant_contours = [c for c in contours if cv2.contourArea(c) > 10]

    if not significant_contours:
        return False

    # Calculate bounding box of ink
    points = np.vstack(contours)

    x, y, w, h = cv2.boundingRect(points)

    if w < 50 or h < 10:
        return False

    # Signature is normally wider than tall
    aspect_ratio = w / h

    if aspect_ratio < 1.5:
        return False

    # 5. Signature should have multiple connected parts
    contour_count = len(contours)
    if contour_count < 1:
        return False

    return True


def get_file_extensions(mime_types):
    return [
        mime_type.split("/")[-1].replace("svg+xml", "svg") for mime_type in mime_types
    ]


# @dataclass
# class ImageCropData:
#     x: float = 0.0
#     y: float = 0.0
#     width: float = 0.0
#     height: float = 0.0

#     @classmethod
#     def from_query(cls):
#         """Query parameters se safely data parse karne ke liye method"""
#         return cls(
#             x=float(get_query_value("positionx") or 0),
#             y=float(get_query_value("positiony") or 0),
#             width=float(get_query_value("width") or 0),
#             height=float(get_query_value("height") or 0),
#         )

#     @classmethod
#     def crop_image(cls, image: Image.Image) -> tuple[bool, Image.Image]:
#         """Image ko safely crop karta hai boundary limits check karke"""
#         img_width, img_height = image.size

#         parameter = cls.from_query()

#         # Zero ya negative crop values check
#         if parameter.width <= 0 or parameter.height <= 0:
#             return False, image

#         left = max(0, round(parameter.x))
#         top = max(0, round(parameter.y))
#         right = min(img_width, round(parameter.x + parameter.width))
#         bottom = min(img_height, round(parameter.y + parameter.height))

#         if left >= right or top >= bottom:
#             return False, image

#         return True, image.crop((left, top, right, bottom))

#     @staticmethod
#     def get_exif(image: Image.Image, metadata: dict = None):
#         # EXIF METADATA LOGIC (NEW)
#         exif = image.getexif()
#         user_meta = metadata or {}

#         # Camera info
#         camera = user_meta.get("camera", {})
#         if camera.get("make"):
#             exif[271] = camera["make"]
#         if camera.get("model"):
#             exif[272] = camera["model"]
#         if camera.get("lens"):
#             exif[42036] = camera["lens"]

#         # Date / Time
#         if user_meta.get("datetime"):
#             exif[36867] = user_meta["datetime"]
#             exif[36868] = user_meta["datetime"]

#         # Orientation, Artist, Description
#         if user_meta.get("orientation"):
#             exif[274] = user_meta["orientation"]

#         if user_meta.get("artist"):
#             exif[315] = user_meta["artist"]

#         if user_meta.get("description"):
#             exif[270] = user_meta["description"]

#         # Default or Custom Software & Copyright
#         exif[305] = user_meta.get("software", "My Image Processor v1.0")
#         exif[33432] = user_meta.get(
#             "copyright", "Copyright © 2026. All rights reserved."
#         )


# {
#                 "camera": {
#                     "make": "MyApp",
#                     "model": "Document Scanner",
#                     "lens": "Unknown",
#                 },
#                 "datetime": "2026:08:23 18:30:00",
#                 "orientation": 1,
#                 "software": "myapplication ",
#                 "description": "Identity verification document",
#                 "artist": "myapplication ",
#                 "copyright": "myapplication ",
#             }


def update_image_metadata(path, metadata):
    with Image.open(path) as image:
        exif = image.getexif()

        # Camera
        camera = metadata.get("camera", {})

        if camera.get("make"):
            exif[271] = camera["make"]  # Make

        if camera.get("model"):
            exif[272] = camera["model"]  # Model

        if camera.get("lens"):
            exif[42036] = camera["lens"]  # LensModel

        # Date / Time
        if metadata.get("datetime"):
            exif[36867] = metadata["datetime"]  # DateTimeOriginal
            exif[36868] = metadata["datetime"]  # DateTimeDigitized

        # Orientation
        if metadata.get("orientation"):
            exif[274] = metadata["orientation"]

        # Software
        if metadata.get("software"):
            exif[305] = metadata["software"]

        # Description
        if metadata.get("description"):
            exif[270] = metadata["description"]

        # Artist
        if metadata.get("artist"):
            exif[315] = metadata["artist"]

        # Copyright
        if metadata.get("copyright"):
            exif[33432] = metadata["copyright"]

        # Save back into same file
        image.save(path, exif=exif)


def build_file_upload_response(file, filename, path):
    return json_response(
        {
            "file": {
                "name": filename,
                "size": file.size,
                "content_type": file.content_type,
            },
            "path": path,
            "uploaded": True,
            "url": f"{app_context.request.url_root}{path}?{int(time.time())}",
        }
    )


def join_with_and(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def file_not_found(field_name: str):
    return json_null_response(
        details={
            "title": "File Not Found",
            "message": f"No file found for field '{field_name}'.",
        },
        code="Ex000041",
    )


def unsupported_file(file, extensions):
    return json_null_response(
        details={
            "title": "Unsupported File Type",
            "file_info": {
                "filename": file.filename,
                "filetype": file.content_type,
            },
            "message": f"Unsupported file type. Use {join_with_and(extensions)}.",
        },
        code="Ex000042",
    )


def file_size_limit(file, max_file_size):
    return json_null_response(
        details={
            "title": "File Size Limit",
            "message": f"File size exceeds {max_file_size} bytes limit.",
        },
        code="Ex000043",
    )


def image_crop_error(field_name: str | None = None):
    return json_null_response(
        details={
            "title": "Image Crop Error",
            "message": f"Unable to crop image for field '{field_name}'.",
        },
        code="Ex000044",
    )


def valid_signature_message():
    return json_null_response(
        details={
            "success": False,
            "title": "Signature Not valid",
            "message": "Please upload a valid signature image.",
        },
        code="Ex000041",
    )


def _value(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


def _gps_decimal(value, ref):
    if not value:
        return None

    try:
        d, m, s = value

        result = _value(d) + _value(m) / 60 + _value(s) / 3600

        if ref in ("S", "W"):
            result = -result

        return result

    except Exception:
        return None


def get_gps(exif):
    try:
        gps = exif.get_ifd(34853)

        if not gps:
            return {}

        gps = {GPSTAGS.get(k, k): v for k, v in gps.items()}

        return gps

    except Exception:
        return {}


def _decode_gps(exif):
    gps = get_gps(exif)

    if not gps:
        return {}

    data = {GPSTAGS.get(k, k): v for k, v in gps.items()}

    result = dict(data)

    latitude = _gps_decimal(data.get("GPSLatitude"), data.get("GPSLatitudeRef"))

    longitude = _gps_decimal(data.get("GPSLongitude"), data.get("GPSLongitudeRef"))

    if latitude is not None:
        result["Latitude"] = latitude

    if longitude is not None:
        result["Longitude"] = longitude

    return result


async def get_file_metadata(source):
    if source is None:
        return {}

    try:
        if hasattr(source, "read"):
            data = await source.read()
        else:
            with open(source, "rb") as f:
                data = f.read()

        with Image.open(BytesIO(data)) as image:

            exif = image.getexif()

            metadata = {TAGS.get(key, key): value for key, value in exif.items()}

            return {
                "file": {
                    "format": image.format,
                    "mode": image.mode,
                    "width": image.width,
                    "height": image.height,
                    "size": len(data),
                },
                "device": {
                    "make": metadata.get("Make"),
                    "model": metadata.get("Model"),
                    "serial": (
                        metadata.get("BodySerialNumber")
                        or metadata.get("CameraSerialNumber")
                    ),
                },
                "camera": {
                    "make": metadata.get("Make"),
                    "model": metadata.get("Model"),
                    "lens_make": metadata.get("LensMake"),
                    "lens_model": metadata.get("LensModel"),
                    "lens_serial": metadata.get("LensSerialNumber"),
                },
                "datetime": {
                    "original": metadata.get("DateTimeOriginal"),
                    "digitized": metadata.get("DateTimeDigitized"),
                    "modified": metadata.get("DateTime"),
                },
                "gps": _decode_gps(exif),
                "image": {
                    "orientation": metadata.get("Orientation"),
                    "color_space": metadata.get("ColorSpace"),
                    "software": metadata.get("Software"),
                    "description": metadata.get("ImageDescription"),
                    "artist": metadata.get("Artist"),
                    "copyright": metadata.get("Copyright"),
                },
                "exif": metadata,
            }

    except Exception as e:
        return {"error": str(e)}


def serialize_media_asset(
    record: Optional[MediaAsset], *, file_type: Optional[str] = None
) -> dict[str, Any]:
    """
    MediaAsset ORM object ko dictionary format me serialize karta hai.
    """
    if record is None:
        return {}

    serialized_data: dict[str, Any] = {
        "id": getattr(record, "id", None),
        "name": getattr(record, "name", ""),
        "src": getattr(record, "src", ""),
        "thumbnail": getattr(record, "thumbnail", {}),
        "size_bytes": getattr(record, "size_bytes", 0),
        "height": getattr(record, "height", 0),
        "width": getattr(record, "width", 0),
        "timestamp": getattr(record, "timestamp", 0),
        "extension": getattr(record, "extension", ""),
    }

    # Determine file type dynamically if not explicitly provided
    resolved_file_type = file_type or getattr(record, "file_type", "")

    # Video assets ke liye duration field attach karein
    if resolved_file_type == "video":
        serialized_data["duration"] = getattr(record, "duration", 0)

    return serialized_data


def get_paginated_files(
    directory_path: str, start: int = 0, end: int = 50
) -> dict[str, Any]:
    """
    Fast system command ka use karke total count batata hai
    aur start se end index ke beech ki file names return karta hai.
    """
    if not os.path.exists(directory_path):
        return {"total": 0, "start": start, "end": end, "files": []}

    current_os = platform.system()
    total_count = 0
    file_names: List[str] = []

    try:
        # =========================================================
        # 1. TOTAL COUNT (FAST SYSTEM COMMANDS)
        # =========================================================
        if current_os == "Windows":
            cmd_count = f'dir "{directory_path}" /b /a:-d | find /c /v ""'
            res_count = subprocess.run(
                cmd_count, shell=True, capture_output=True, text=True, check=True
            )
            total_count = int(res_count.stdout.strip())

        elif current_os in ["Linux", "Darwin"]:
            cmd_count = f'ls -1U "{directory_path}" | wc -l'
            res_count = subprocess.run(
                cmd_count, shell=True, capture_output=True, text=True, check=True
            )
            total_count = int(res_count.stdout.strip())

        # =========================================================
        # 2. FETCH FILE NAMES BETWEEN START AND END
        # =========================================================
        # Note: Linux/Mac me sed command se exact lines extract hoti hain
        # 1-based indexing handle karne ke liye (start + 1)
        line_start = start + 1
        line_end = end

        if current_os in ["Linux", "Darwin"] and line_start <= line_end:
            cmd_files = f'ls -1U "{directory_path}" | sed -n "{line_start},{line_end}p"'
            res_files = subprocess.run(
                cmd_files, shell=True, capture_output=True, text=True, check=True
            )
            file_names = [
                name for name in res_files.stdout.splitlines() if name.strip()
            ]

        else:
            # Windows ya Fallback Stream Generator (Memory Safe Slicing)
            with os.scandir(directory_path) as entries:
                files_gen = (entry.name for entry in entries if entry.is_file())

                # Agar count command fail hua tha toh total yahi se calculate ho jayega
                if total_count == 0:
                    all_files = list(files_gen)
                    total_count = len(all_files)
                    file_names = all_files[start:end]
                else:
                    # Direct slice via iterator
                    file_names = []
                    for idx, name in enumerate(files_gen):
                        if idx >= end:
                            break
                        if idx >= start:
                            file_names.append(name)

    except Exception:
        # Fallback agar command fail ho jaye
        with os.scandir(directory_path) as entries:
            all_files = [entry.name for entry in entries if entry.is_file()]
            total_count = len(all_files)
            file_names = all_files[start:end]

    return {"total": total_count, "start": start, "end": end, "files": file_names}
