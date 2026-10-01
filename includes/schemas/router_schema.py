from dataclasses import dataclass, field
from typing import Optional, List,  Any
from urllib.parse import unquote, urlparse


@dataclass
class DynamicURLRoute:
    """
    Universal Dynamic URL Route Parser.
    Handles up to 7 fixed URL depth levels (without primary_context).
    """

    raw_path: str  # Original URL path
    depth: int  # Total path segments count (1 to 7)

    # 7 Fixed Level Parameters
    scope_type: Optional[str] = (
        None  # Segment 1: e.g. 'category', 'practice', 'questions', 'exams'
    )
    scope_slug: Optional[str] = (
        None  # Segment 2: e.g. 'jharkhand-gk', 'upsc-2026', 'education'
    )
    resource_type: Optional[str] = (
        None  # Segment 3: e.g. 'mock-test', 'chapter-1', 'mcq'
    )
    resource_slug: Optional[str] = (
        None  # Segment 4: e.g. 'what-is-article-370', 'question-101'
    )
    sub_action: Optional[str] = None  # Segment 5: e.g. 'view', 'start', 'download'
    child_entity: Optional[str] = (
        None  # Segment 6: e.g. 'solutions', 'comments', 'result'
    )
    modifier: Optional[str] = None  # Segment 7: e.g. 'pdf', 'attempt-1', 'v2'

    # Dynamic raw segments list for fallback
    segments: List[str] = field(default_factory=list)

    @classmethod
    def parse(cls, url_path: str) -> "DynamicURLRoute":
        """
        Parses URL path into 7 structured parameters starting from scope_type.
        """
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
            scope_type=segments[0] if depth > 0 else None,  # Segment 1
            scope_slug=segments[1] if depth > 1 else None,  # Segment 2
            resource_type=segments[2] if depth > 2 else None,  # Segment 3
            resource_slug=segments[3] if depth > 3 else None,  # Segment 4
            sub_action=segments[4] if depth > 4 else None,  # Segment 5
            child_entity=segments[5] if depth > 5 else None,  # Segment 6
            modifier=segments[6] if depth > 6 else None,  # Segment 7
            segments=segments,
        )

    def get_route_summary(self) -> dict[str, Any]:
        """Helper method to return active route properties as dictionary."""
        return {
            k: v for k, v in self.__dict__.items() if v is not None and k != "segments"
        }
