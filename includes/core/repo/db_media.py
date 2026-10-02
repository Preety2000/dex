import os
import math
import posixpath
import fitz
import hashlib
import mimetypes
from io import BytesIO
from datetime import datetime
from typing import Any, List
from contextlib import contextmanager

from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Project specific imports (modify according to your project structure)
from includes.database.sql import LocalDB
from includes.core.repo.thumbnail import Thumbnail
from includes.database.media_asset_model import MediaAsset, MediaAssetBase
from includes.utils.file import serialize_media_asset
from includes.db.models.utils import TimeStamp

# MIME TYPES MAPPING & HELPER

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
        "application/vnd.pdf",  # Vendor-specific type
    ],
}


def detect_category_from_mime(mime_type: str) -> str:
    """MIME_TYPES mapping se media_type detect karta hai."""
    if not mime_type:
        return "other"

    for cat, mimes in MIME_TYPES.items():
        if mime_type in mimes:
            return cat

    # Fallback checking based on prefix
    if mime_type.startswith("image/"):
        return "image"
    elif mime_type.startswith("video/"):
        return "video"
    elif mime_type.startswith("audio/"):
        return "audio"

    return "other"


# 2. LOCAL DATABASE MANAGER
class TableRegistry:
    pass


# 3. HELPER FUNCTIONS


def calculate_file_hash(file_path: str) -> str:
    """MD5 file hash calculate karta hai duplicate files detect karne ke liye."""
    hasher = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


def get_media_duration(file_path: str, mime_type: str) -> int:
    """PDF / Audio / Video ke liye duration/pages calculate karta hai."""
    try:
        if mime_type in MIME_TYPES["pdf"]:
            doc = fitz.open(file_path)
            pages = len(doc)
            doc.close()
            return pages  # PDF ke liye total pages store honge
    except Exception:
        pass
    return 0


# MEDIA MANAGER SERVICE
class MediaManager:

    @staticmethod
    def _get_db():
        return LocalDB("DB_FILES", MediaAssetBase, "db_media")

    @staticmethod
    def calculate_file_size(file_path: str):
        size_bytes = os.stat(file_path).st_size
        if size_bytes == 0:
            return 0, "0B"

        size_name = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return size_bytes, f"{s} {size_name[i]}"

    @staticmethod
    def get_image_dimensions(file_path: str):
        try:
            with Image.open(file_path) as img:
                return img.width, img.height
        except Exception:
            return None, None

    @staticmethod
    def parse_file_metadata(
        file: str,
        directory_path: str,
        media_type: str = None,
        is_public: bool = True,
        storage_provider: str = "local",
    ):
        file_path = posixpath.join(directory_path, file)
        stat = os.stat(file_path)

        size_bytes, file_size = MediaManager.calculate_file_size(file_path)
        width, height = MediaManager.get_image_dimensions(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)

        if media_type is None:
            media_type = detect_category_from_mime(mime_type)

        thumbnail = Thumbnail.create(file_path=file_path, size=(2 * 1024))
        ext = file.rsplit(".", 1)[-1].lower() if "." in file else ""
        file_hash = calculate_file_hash(file_path)
        duration = get_media_duration(file_path, mime_type or "")

        return {
            "name": file,
            "src": f"/media/{media_type}/{file}",
            "thumbnail": thumbnail.get("data_url", ""),
            "file_type": mime_type or "application/octet-stream",
            "size_bytes": size_bytes,
            "height": height or thumbnail.get("height", 0),
            "width": width or thumbnail.get("width", 0),
            "original_height": height or thumbnail.get("height", 0),
            "original_width": width or thumbnail.get("width", 0),
            "original_timestamp": int(stat.st_mtime),
            "timestamp": TimeStamp.now_timestamp(),
            "extension": ext,
            "duration": duration,
            "storage_provider": storage_provider,
            "file_hash": file_hash,
            "is_public": is_public,
            "status": "completed",
            "is_deleted": False,
            "size_formatted": file_size,
            "directory_path": directory_path,
        }

    @classmethod
    def _sync_to_database(cls, meta: dict):
        """db instance bahar se pass hoga"""
        db = cls._get_db()
        if not db or not MediaAsset:
            return

        with db.session_scope() as session:
            existing = session.query(MediaAsset).filter_by(src=meta["src"]).first()

            print(meta["directory_path"])

            if not existing:
                db_entry = MediaAsset(
                    name=meta["name"],
                    src=meta["src"],
                    thumbnail=meta["thumbnail"],
                    file_type=meta["file_type"],
                    size_bytes=meta["size_bytes"],
                    height=meta["height"],
                    width=meta["width"],
                    original_height=meta["original_height"],
                    original_width=meta["original_width"],
                    original_timestamp=meta["original_timestamp"],
                    timestamp=meta["timestamp"],
                    extension=meta["extension"],
                    duration=meta["duration"],
                    storage_provider=meta["storage_provider"],
                    file_hash=meta["file_hash"],
                    is_public=meta["is_public"],
                    status=meta["status"],
                    is_deleted=meta["is_deleted"],
                )
                session.add(db_entry)

    @staticmethod
    async def sync_library(directory_path: str, media_type: str = None):
        files_metadata = []

        if not os.path.exists(directory_path):
            return {"status": "error", "message": "Directory not found", "data": []}

        for file in os.listdir(directory_path):
            file_path = posixpath.join(directory_path, file)
            if os.path.isfile(file_path):
                meta = MediaManager.parse_file_metadata(
                    file=file,
                    media_type=media_type,
                    directory_path=directory_path,
                )
                files_metadata.append(meta)

                MediaManager._sync_to_database(meta)

        return {
            "status": "success",
            "total_files": len(files_metadata),
            "files": files_metadata,
        }

    @classmethod
    async def sync_files(
        cls, directory_path: str, missing_files: List[str], media_type: str = None
    ) -> List[MediaAsset]:
        db = cls._get_db()
        if not missing_files or not db:
            return []

        parsed_metadata_list = []
        for file in missing_files:
            file_path = posixpath.join(directory_path, file)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                meta = MediaManager.parse_file_metadata(
                    file=file,
                    media_type=media_type,
                    directory_path=directory_path,
                )
                parsed_metadata_list.append(meta)

        if not parsed_metadata_list:
            return []

        created_assets: List[MediaAsset] = []

        with db.session_scope() as session:
            session.bulk_insert_mappings(MediaAsset, parsed_metadata_list)
            session.flush()

            inserted_names = [m["name"] for m in parsed_metadata_list]
            created_assets = (
                session.query(MediaAsset)
                .filter(MediaAsset.name.in_(inserted_names))
                .all()
            )

        return created_assets

    @classmethod
    async def fetch_or_sync_assets(
        cls, directory_path: str, target_filenames: List[str] = None
    ) -> List[dict[str, Any]]:
        """
        Database se existing media assets fetch karta hai.
        Jo files DB me missing hain unhe scan karke DB me sync/insert karta hai
        aur sabhi serialized assets ko merge karke return karta hai.
        """

        if not target_filenames:
            return []

        db = cls._get_db()
        resolved_assets: List[dict[str, Any]] = []

        with db.session_scope() as session:
            db_records = (
                session.query(MediaAsset)
                .filter(MediaAsset.name.in_(target_filenames))
                .all()
            )

            found_names = set()
            for record in db_records:
                found_names.add(record.name)
                resolved_assets.append(serialize_media_asset(record))

            missing_filenames = [
                name for name in target_filenames if name not in found_names
            ]

        # Missing files ko parse karke sync karein
        if missing_filenames:
            newly_created_assets = await cls.sync_files(
                directory_path=directory_path,
                missing_files=missing_filenames,
            )
            for asset in newly_created_assets:
                resolved_assets.append(serialize_media_asset(asset))

        return resolved_assets
