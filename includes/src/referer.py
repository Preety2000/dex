import uuid
from typing import Optional
from dataclasses import field
from urllib.parse import parse_qs, urlparse
from attr import dataclass

@dataclass(init=False)
class Referer:
    path: str = ""
    query: str = ""
    params: dict = field(default_factory=dict)

    base_url: str = ""
    base_uri: str = ""
    full_path: str = ""
    url_root: str = ""
    host_url: str = ""
    request_id: str = ""

    depth: int = 0
    raw_path: str = ""

    section: Optional[str] = None
    scope: Optional[str] = None
    entity: Optional[str] = None
    action: Optional[str] = None
    core: Optional[str] = None
    space: Optional[str] = None
    end: Optional[str] = None

    def __new__(cls, request):
        if request.headers.get("Referer") is None:
            return None

        return super().__new__(cls)

    def __init__(self, request):
        referer_url = request.headers.get("Referer")
        parsed = urlparse(referer_url)

        scheme = parsed.scheme or "http"
        netloc = parsed.netloc

        self.path = parsed.path
        self.query = parsed.query

        raw_params = parse_qs(self.query)
        self.params = {
            key: values[0] if len(values) == 1 else values
            for key, values in raw_params.items()
        }

        self.url_root = f"{scheme}://{netloc}"
        self.base_url = f"{self.url_root}{self.path}"
        self.base_uri = self.base_url
        self.full_path = (
            f"{self.base_url}?{self.query}" if self.query else self.base_url
        )
        self.host_url = f"{self.url_root}/"
        self.request_id = str(uuid.uuid4())

        self.raw_path = self.path.strip("/")
        parts = self.raw_path.split("/") if self.raw_path else []
        self.depth = len(parts)

        fields = ("section", "scope", "entity", "action", "core", "space", "end")
        for index, name in enumerate(fields):
            setattr(self, name, parts[index] if index < len(parts) else None)
