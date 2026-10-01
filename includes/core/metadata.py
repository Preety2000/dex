import json
import os
from functools import lru_cache
from datetime import datetime
from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict
from includes.core.repo.dir_manager import folder


# @lru_cache Decorator (Synchronous Function)
@lru_cache(maxsize=1)
def get_config_metadata() -> dict:
    filepath = os.path.join(folder.static_json, "config.json")

    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)

    return {}


@dataclass
class Metadata:
    # --- Basic Content Metadata ---
    title: str | None = None
    excerpt: str | None = None
    description: str | None = None  # SEO Meta Description
    keywords: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    category: str | None = None
    language: str | None = "en"  # e.g., 'en-US', 'hi-IN'

    # --- Author & Publishing Details ---
    author: str | None = None
    publisher: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # --- URL & Navigation ---
    canonical_url: str | None = None
    redirect_url: str | None = None
    site_url: str | None = None
    site_name: str | None = "MyApplication"
    site_domain: str | None = None

    # --- Media & Visuals ---
    cover_image: str | None = None  # Main page/article banner image URL
    thumbnail: str | None = None
    favicon: str | None = None

    # --- SEO & Web Crawling Directives ---
    robots: str | None = "index, follow"  # e.g., 'noindex, nofollow'
    follow_link: dict[str, str] = field(default_factory=dict)

    # --- Open Graph (Facebook / LinkedIn / WhatsApp) ---
    og_title: str | None = None
    og_description: str | None = None
    og_image: str | None = None
    og_type: str | None = "article"  # 'website', 'article', 'profile'
    og_locale: str | None = "en_US"

    # --- Twitter Cards ---
    twitter_card: str | None = "summary_large_image"
    twitter_site: str | None = None  # e.g., '@yourhandle'
    twitter_creator: str | None = None
    twitter_image: str | None = None

    # --- App / System Configuration ---
    app_mail: str | None = "studyhub@mail.com"
    template: str | None = None
    settings: list = field(default_factory=list)
    custom_meta: dict[str, str] = field(default_factory=dict)  # Any extra <meta> tags

    # Config Load Method
    def load_config(self, force_reload: bool = False) -> "Metadata":
        if force_reload:
            get_config_metadata.cache_clear()

        config = get_config_metadata()
        for field_name in asdict(self):
            if field_name in config:
                setattr(self, field_name, config[field_name])
        return self

    # Reset Method
    async def reset(self, reload_json: bool = False) -> "Metadata":
        # Global default values restore karna
        default_instance = Metadata()
        for field_name in asdict(default_instance):
            setattr(self, field_name, getattr(default_instance, field_name))

        # Fresh config load karna
        self.load_config(force_reload=reload_json)
        return self

    def to_dict(self) -> dict:
        return asdict(self)

    # Instance Method for Updating Attributes
    def update_from_dict(self, data: Dict[str, Any]) -> "Metadata":
        """Dictionary se Metadata instance attributes ko update karta hai."""
        if not data or not isinstance(data, dict):
            return self

        valid_fields = {f.name for f in fields(self)}

        for key, value in data.items():
            if key in valid_fields:
                # ISO DateTime string ko wapas datetime object me convert karna
                if key in ("created_at", "updated_at") and isinstance(value, str):
                    try:
                        value = datetime.fromisoformat(value)
                    except ValueError:
                        pass
                setattr(self, key, value)

        return self


# Global Instance
MetaData = Metadata(title="Error 404")


async def set_article_context(data: dict) -> None:
    """
    Update metadata fields using article-specific data.
    Only existing metadata attributes are updated.
    """
    for field in asdict(MetaData):
        if field in data:
            setattr(MetaData, field, data[field])
