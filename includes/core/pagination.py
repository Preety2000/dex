import inspect
from dataclasses import is_dataclass
from typing import Any, Callable
from urllib.parse import parse_qs, urlencode

from includes.core.globals.entry import app_context
from includes.db.dataclass import serialize
from includes.db.models.owner import Members
from includes.src.request import RequestContext
from includes.utils.utils import (
    get_referer,
    get_post_value,
    get_query_value,
    get_referer_value,
)


def parse_int(value: int | str | None, default: int | None = None) -> int | None:
    """Safely convert a value to int."""
    if value is None or value == "":
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def set_serial_number(item: dict | Any, number: int):
    """Set serial number on a dict or dataclass instance."""
    if isinstance(item, dict):
        item["sno"] = number

    elif is_dataclass(item):
        item.sno = number

    else:
        raise TypeError(f"item must be dict or dataclass, got {type(item).__name__}")

    return item


def build_pagination_url(
    name: str,
    css_class: str,
    page: int,
    request: RequestContext,
) -> dict:
    """Build pagination item with the requested page number."""

    base_url = (
        request.host_url + "resent"
        if request.host_url == request.base_uri
        else request.base_uri
    )

    query_params = parse_qs(request.query)

    # Remove existing page parameter.
    query_params.pop("page", None)

    # Add requested page.
    query_params["page"] = [page]

    query_string = urlencode(query_params, doseq=True)
    url = f"{base_url}?{query_string}"

    return {
        "name": name,
        "clas": css_class,
        "slug": url,
        "page": page,
    }


class Pagination:
    """Reusable pagination handler for query, API and referer requests."""

    def __init__(self, request_type: str | None = None):
        request_type = request_type or "query"

        if request_type == "query":
            self.url = app_context.request
            self.callback = get_query_value

        elif request_type == "api":
            self.url = app_context.request
            self.callback = get_post_value

        elif request_type == "referer":
            self.url = get_referer()
            self.callback = get_referer_value

        else:
            raise ValueError(
                f"Invalid request_type: {request_type!r}. "
                "Expected: 'query', 'api', or 'referer'."
            )

        self.page: int | None = None
        self.limit: int | None = None

    def set_page_limit(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> None:
        """Set valid page and limit values."""

        if isinstance(limit, int) and limit > 0:
            self.limit = limit

        if isinstance(page, int) and page > 0:
            self.page = page

    async def load(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
    ):
        """Load page and limit values from the configured request source."""

        self.set_page_limit(limit=limit, page=page)

        page = self.callback("page")
        limit = self.callback("limit")

        if inspect.isawaitable(page):
            page = await page

        if inspect.isawaitable(limit):
            limit = await limit

        page = parse_int(page)
        limit = parse_int(limit)

        if isinstance(page, int):
            self.page = page

        if isinstance(limit, int):
            self.limit = limit

        return self

    def get_offset(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> int:
        """Return database offset for the current page."""

        self.set_page_limit(limit=limit, page=page)

        if self.page is None or self.limit is None:
            return 0

        return (self.page - 1) * self.limit

    async def paginate(
        self,
        *,
        total: int = 0,
        limit: int = 10,
        data: list | None = None,
        transform: Callable | None = None,
    ):
        """
        Generate paginated data and pagination navigation.

        Returns:
            If data is provided:
                (processed_data, pagination, total)

            Otherwise:
                (pagination, total)
        """

        # Use supplied limit only when no limit was loaded from request.
        if self.limit is None:
            self.limit = limit

        if self.page is None:
            self.page = 1

        # Protect against invalid values.
        if self.limit <= 0:
            self.limit = limit

        if self.page <= 0:
            self.page = 1

        total_pages = (total + self.limit - 1) // self.limit

        pagination = []

        # Process data and assign serial numbers.
        processed_data = None

        if data is not None:
            offset = self.get_offset()

            processed_data = []

            for index, item in enumerate(data):
                if callable(transform):
                    item = transform(item)

                    if inspect.isawaitable(item):
                        item = await item

                if not isinstance(item, dict):
                    item = serialize(item)

                processed_data.append(
                    set_serial_number(
                        item,
                        offset + index + 1,
                    )
                )

        # Previous page.
        if self.page > 1:
            pagination.append(
                build_pagination_url(
                    "Prev",
                    "deactive",
                    self.page - 1,
                    self.url,
                )
            )

        # Page number range.
        start_page = max(1, self.page - 2)
        end_page = min(total_pages, self.page + 2)

        for page_number in range(start_page, end_page + 1):
            pagination.append(
                build_pagination_url(
                    page_number,
                    "active" if page_number == self.page else "deactive",
                    page_number,
                    self.url,
                )
            )

        # Next page.
        if self.page < total_pages:
            pagination.append(
                build_pagination_url(
                    "Next",
                    "deactive",
                    self.page + 1,
                    self.url,
                )
            )

        # Last page.
        if total_pages > 1 and self.page < total_pages:
            pagination.append(
                build_pagination_url(
                    "Last",
                    "deactive",
                    total_pages,
                    self.url,
                )
            )

        if data is not None:
            return processed_data, pagination, total

        return pagination, total

    @classmethod
    async def get_paginate(
        cls,
        *,
        limit: int = 10,
        query: Any | None = None,
        transform: callable = None,
        order_by: Any | None = None,
        request_type: str | None = None,
    ):
        total_count = query.count()
        paginator = cls(request_type)
        await paginator.load(limit=limit)
        offset = paginator.get_offset()

        if order_by is not None:
            query = query.order_by(order_by)

        # print("BEFORE pagination:", query.count())

        records = query.offset(offset).limit(paginator.limit).all()

        # print("AFTER pagination:", len(records))

        data, paginator, results = await paginator.paginate(
            total=total_count,
            data=records,
            transform=transform,
        )
        return data, paginator, results
