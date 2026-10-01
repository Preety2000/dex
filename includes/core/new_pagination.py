import inspect
from dataclasses import is_dataclass
from typing import Any, Callable, Optional, Tuple
from urllib.parse import parse_qs, urlencode
from sqlalchemy import func, select

from includes.core.globals.entry import app_context
from includes.db.connection import active_secondary_db
from includes.db.dataclass import serialize
from includes.src.request import RequestContext
from includes.utils.utils import (
    get_post_value,
    get_query_value,
    get_referer,
    get_referer_value,
)


def parse_int(value: int | str | None, default: int | None = None) -> int | None:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def set_serial_number(item: dict | Any, number: int):
    if isinstance(item, dict):
        item["sno"] = number
    elif is_dataclass(item):
        item.sno = number
    else:
        raise TypeError(f"item must be dict or dataclass, got {type(item).__name__}")
    return item


def build_pagination_url(
    name: Any,
    css_class: str,
    page: int,
    request: Any,
) -> dict:
    if not request:
        return {
            "name": str(name),
            "clas": css_class,
            "slug": f"?page={page}",
            "page": page,
        }

    base_url = (
        getattr(request, "host_url", "") + "resent"
        if getattr(request, "host_url", None) == getattr(request, "base_uri", None)
        else getattr(request, "base_uri", "")
    )

    raw_query = getattr(request, "query", "")
    if isinstance(raw_query, str):
        query_params = parse_qs(raw_query)
    elif isinstance(raw_query, dict):
        query_params = raw_query.copy()
    else:
        query_params = {}

    query_params["page"] = [page]
    query_string = urlencode(query_params, doseq=True)
    url = f"{base_url}?{query_string}" if base_url else f"?{query_string}"

    return {
        "name": str(name),
        "clas": css_class,
        "slug": url,
        "page": page,
    }


class Pagination:
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
        self.set_page_limit(limit=limit, page=page)

        page_val = self.callback("page")
        limit_val = self.callback("limit")

        if inspect.isawaitable(page_val):
            page_val = await page_val
        if inspect.isawaitable(limit_val):
            limit_val = await limit_val

        page_val = parse_int(page_val)
        limit_val = parse_int(limit_val)

        if isinstance(page_val, int) and page_val > 0:
            self.page = page_val

        if isinstance(limit_val, int) and limit_val > 0:
            self.limit = limit_val

        return self

    def get_offset(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> int:
        self.set_page_limit(limit=limit, page=page)
        p = self.page if (self.page and self.page > 0) else 1
        l = self.limit if (self.limit and self.limit > 0) else 10
        return (p - 1) * l

    async def paginate(
        self,
        *,
        total: int = 0,
        limit: int = 10,
        data: list | None = None,
        transform: Callable | None = None,
    ):
        if self.limit is None or self.limit <= 0:
            self.limit = limit
        if self.page is None or self.page <= 0:
            self.page = 1

        total_pages = max(1, (total + self.limit - 1) // self.limit)
        pagination = []
        processed_data = None

        if data is not None:
            offset = self.get_offset()
            processed_data = []

            for index, item in enumerate(data):
                if callable(transform):
                    item = transform(item)
                    if inspect.isawaitable(item):
                        item = await item

                if not isinstance(item, dict) and not is_dataclass(item):
                    item = serialize(item)

                processed_data.append(
                    set_serial_number(
                        item,
                        offset + index + 1,
                    )
                )

        # Navigation Links
        if self.page > 1:
            pagination.append(
                build_pagination_url("Prev", "deactive", self.page - 1, self.url)
            )

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

        if self.page < total_pages:
            pagination.append(
                build_pagination_url("Next", "deactive", self.page + 1, self.url)
            )

        if total_pages > 1 and self.page < total_pages:
            pagination.append(
                build_pagination_url("Last", "deactive", total_pages, self.url)
            )

        if data is not None:
            return processed_data, pagination, total

        return pagination, total

    @classmethod
    async def get_paginate(
        cls,
        *,
        limit: int = 10,
        query: Any = None,
        transform: Optional[Callable] = None,
        order_by: Any | None = None,
        request_type: str | None = None,
        db: Any | None = None,
    ) -> Tuple[list, list, int]:
        """SQLAlchemy select() compatible async paginator execution."""

        # 1. Resolve DB Session safely
        db = db or active_secondary_db()
        if inspect.isawaitable(db):
            db = await db

        # 2. Total Count Calculation for select()
        if hasattr(query, "subquery"):
            count_stmt = select(func.count()).select_from(
                query.order_by(None).subquery()
            )

            # Safe Execution (Handles both Sync and Async DB drivers)
            result = db.execute(count_stmt)
            if inspect.isawaitable(result):
                result = await result

            total_count = result.scalar() or 0
        else:
            # Fallback for legacy query objects
            total_count = query.count()
            if inspect.isawaitable(total_count):
                total_count = await total_count

        # 3. Paginator Setup
        paginator = cls(request_type)
        await paginator.load(limit=limit)
        offset = paginator.get_offset()

        # 4. Order By & Offset/Limit Application
        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(offset).limit(paginator.limit)

        # 5. Fetch Records safely
        if hasattr(query, "subquery"):
            res = db.execute(query)
            if inspect.isawaitable(res):
                res = await res
            records = res.scalars().all()
        else:
            records = query.all()
            if inspect.isawaitable(records):
                records = await records

        # 6. Process Paginated Result
        data, pagination, results = await paginator.paginate(
            total=total_count,
            data=records,
            transform=transform,
        )

        return data, pagination, results
