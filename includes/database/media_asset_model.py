from sqlalchemy import Column, Integer, String, BigInteger, Boolean, create_engine
from sqlalchemy.orm import declarative_base

from includes.db.models.utils import TimeStamp

MediaAssetBase = declarative_base()


class MediaAsset(MediaAssetBase):
    __tablename__ = "media_assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    src = Column(String(500), nullable=False)
    thumbnail = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=True)

    size_bytes = Column(BigInteger, default=0)

    # Processed / Compressed Dimensions
    height = Column(Integer, default=0)
    width = Column(Integer, default=0)

    # Original Dimensions
    original_height = Column(Integer, default=0)
    original_width = Column(Integer, default=0)
    original_timestamp = Column(BigInteger, default=0)

    # System Timestamp
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    # File Metadata & Extensions
    extension = Column(String(10), nullable=True)
    duration = Column(Integer, default=0)  # Video/Audio duration (seconds)

    # Storage Details / "s3", "local", "cloudinary"
    storage_provider = Column(String(50), default="local")
    root_detail = Column(String(100), nullable=True)
    file_hash = Column(String(64), nullable=True)  # Duplicate detection (MD5)

    # User & Access Control
    user_id = Column(Integer, index=True, nullable=True)  # File owner ID
    is_public = Column(Boolean, default=True)  # Public/Private access

    # Processing & Status / "pending", "processing", "completed", "failed"
    status = Column(String(20), default="completed")
    is_deleted = Column(Boolean, default=False)
