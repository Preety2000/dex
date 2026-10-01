from __future__ import annotations
from typing import Any, Optional
from urllib.parse import parse_qs

from includes.core.globals.entry import app_context
from includes.src.request import RequestContext


class Referer:
    """
    Convenience facade for accessing the current request's referer context.
    Examples:
        Referer.get()
        Referer.path
        Referer.resource
        Referer.get_search("page")
        Referer.get_search_int("page")
    """

    @classmethod
    def _context(cls) -> Optional[RequestContext]:
        """Return the current referer context, if available."""
        try:
            return app_context.request.referer
        except AttributeError:
            return None

    @classmethod
    def get(cls) -> Optional[RequestContext]:
        """Return the complete referer RequestContext."""
        return cls._context()

    @classmethod
    def __getattr__(cls, name: str) -> Any:
        """
        Proxy unknown attributes to the current referer context.

        Note:
            Python does not normally use __getattr__ on a class itself
            for `Referer.path`, so a metaclass/property approach would be
            required for true class-level transparent proxying.
        """
        context = cls._context()

        if context is None:
            return None

        return getattr(context, name, None)

    @classmethod
    def get_search(cls, name: str, default: Any = None) -> Any:
        """
        Get a single query parameter from the referer's query string.

        Returns:
            The first value when query params are strings.
            A direct value when params behaves like a mapping.
            `default` when the value does not exist.
        """
        context = cls._context()

        if context is None or not name:
            return default

        params = getattr(context, "params", None)

        if not params:
            return default

        try:
            if isinstance(params, str):
                values = parse_qs(
                    params,
                    keep_blank_values=True,
                )
                values = values.get(name)

                return values[0] if values else default

            if hasattr(params, "get"):
                value = params.get(name, default)

                # Mapping may return a list, similar to parse_qs().
                if isinstance(value, (list, tuple)):
                    return value[0] if value else default

                return value

        except (TypeError, ValueError, AttributeError):
            return default

        return default

    @classmethod
    def get_search_int(
        cls,
        name: str,
        default: Optional[int] = None,
    ) -> Optional[int]:
        """Get a query parameter as an integer."""
        value = cls.get_search(name)

        if value is None or value == "":
            return default

        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @classmethod
    def get_search_float(
        cls,
        name: str,
        default: Optional[float] = None,
    ) -> Optional[float]:
        """Get a query parameter as a float."""
        value = cls.get_search(name)

        if value is None or value == "":
            return default

        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @classmethod
    def has_search(cls, name: str) -> bool:
        """Check whether a query parameter exists."""
        return cls.get_search(name, default=None) is not None
