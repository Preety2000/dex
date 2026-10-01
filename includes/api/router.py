from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlparse


@dataclass
class DynamicSokitURLRoute:
    raw_path: str
    depth: int

    # 5 Fixed Level Parameters
    scope_type: Optional[str] = None
    scope_slug: Optional[str] = None
    resource_type: Optional[str] = None
    resource_slug: Optional[str] = None
    action: Optional[str] = None

    # Complete decoded segments list
    segments: List[str] = field(default_factory=list)

    @classmethod
    def parse(cls, url_path: str) -> "DynamicSokitURLRoute":
        parsed_url = urlparse(url_path)
        clean_path = parsed_url.path.strip("/")

        if not clean_path:
            return cls(raw_path=url_path, depth=0, segments=[])

        # Extract and decode all path segments
        raw_segments = clean_path.split("/")
        segments = [unquote(seg) for seg in raw_segments if seg]
        depth = len(segments)

        return cls(
            raw_path=url_path,
            depth=depth,
            scope_type=segments[0] if depth > 0 else None,
            scope_slug=segments[1] if depth > 1 else None,
            resource_type=segments[2] if depth > 2 else None,
            resource_slug=segments[3] if depth > 3 else None,
            action=segments[4] if depth > 4 else None,
            segments=segments,
        )

    def get_route_summary(self) -> Dict[str, Any]:
        """Helper method to return active route properties as dictionary."""
        return {
            k: v for k, v in self.__dict__.items() if v is not None and k != "segments"
        }
