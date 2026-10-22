from dataclasses import dataclass, field
from typing import Optional, List, Union
from urllib.parse import urlparse, unquote
from includes.src.request import Request

# Dynamic level field mapping (Index 0 to 6)
LEVEL_FIELDS = ("section", "scope", "entity", "action", "core", "space", "end")


@dataclass
class Route:
    """
    Universal Dynamic URL Route Parser.

    - Initialization: Direct `Request` object ya string path se instance banayein.
    - Reusability: `reset()` ko call karke request ya path pass karke reuse karein.
    """

    raw_path: str = ""
    depth: int = 0

    # Fixed Level Parameters (Up to 7 levels)
    section: Optional[str] = None
    scope: Optional[str] = None
    entity: Optional[str] = None
    action: Optional[str] = None
    core: Optional[str] = None
    space: Optional[str] = None
    end: Optional[str] = None

    # Dynamic raw segments
    segments: List[str] = field(default_factory=list)

    def __post_init__(self):
        """
        Dataclass create hote hi agar raw_path pass hua hai
        (jaise Request object ya URL path string) to use parse kar dega.
        """
        if self.raw_path:
            self.reset(self.raw_path)

    def reset(self, target: Union[Request, str]) -> "Route":
        """
        URL ya Request object ko parse karke current instance update karta hai.
        Accepts: `Request` object OR `str` path.
        """
        # Input standard path string mein normalize karein
        if isinstance(target, Request):
            path_str = target.url.path
        else:
            path_str = str(target) if target else ""

        self.raw_path = path_str
        parsed_url = urlparse(path_str)
        clean_path = parsed_url.path.strip("/")

        # Safe segment extraction and decoding
        if clean_path:
            self.segments = [unquote(s) for s in clean_path.split("/") if s]
        else:
            self.segments = []

        self.depth = len(self.segments)

        # Pre-calculated levels set karein aur missing levels ko None reset karein
        for i, field_name in enumerate(LEVEL_FIELDS):
            value = self.segments[i] if i < self.depth else None
            setattr(self, field_name, value)

        return self


# FastAPI dependency function (Optional helper)
def get_route_context(request: Request) -> Route:
    return Route(request)
