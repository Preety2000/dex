from dataclasses import dataclass, field
from typing import Any

from attr import asdict
from fastapi import Request


@dataclass
class PageContext:
    """
    Page Rendering Context

    किसी page/template को render करने के लिए आवश्यक
    सभी common data यहाँ store किया जा सकता है।
    """

    # Page basic information
    title: str = ""
    excerpt: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)

    # SEO
    site_name: str = "MyApplication"
    site_url: str = ""
    site_domain: str = ""
    canonical_url: str = ""
    robots: str = "index,follow"

    # Open Graph (Facebook, WhatsApp)
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""

    # Twitter Card
    twitter_title: str = ""
    twitter_description: str = ""
    twitter_image: str = ""
    follow_link: list[str] = field(default_factory=list)

    # Template Information
    template: str = ""

    # Current URL
    url: str = ""

    # Page language
    language: str = "hi"

    # Theme
    theme: str = "default"

    # User Data
    member: Any = None

    # Navigation/Menu
    menu: list[Any] = field(default_factory=list)

    # Breadcrumb
    breadcrumb: list[Any] = field(default_factory=list)

    # Page specific data
    data: dict[str, Any] = field(default_factory=dict)

    # Extra metadata
    meta: dict[str, Any] = field(default_factory=dict)

    # CSS Files
    css: list[str] = field(default_factory=list)

    # JavaScript Files
    js: list[str] = field(default_factory=list)

    # Inline JS variables
    js_data: dict[str, Any] = field(default_factory=dict)

    # SVG Icons
    icons: dict[str, Any] = field(default_factory=dict)

    # Custom bindings
    bind: dict[str, Any] = field(default_factory=dict)

    # Status
    status_code: int = 200

    # Cache settings
    cacheable: bool = True

    # Custom headers
    request: Request = None

    # Custom headers
    headers: dict[str, str] = field(default_factory=dict)

    def add(self, key: str, value: Any) -> None:
        """
        PageContext में value set करें। यदि attribute मौजूद नहीं है तो error दें।
        """

        if key not in self.__dataclass_fields__:
            print(f"'{key}' PageContext का valid attribute नहीं है.")

        setattr(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        """
        PageContext को dictionary में convert करें। Example: page.to_dict()
        """

        return {
            field_name: getattr(self, field_name)
            for field_name in self.__dataclass_fields__
        }
