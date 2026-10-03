import inspect
from dataclasses import dataclass
from typing import Any, Callable, Optional
from sqlalchemy import asc, desc
from includes.core.pagination import Pagination
from includes.core.request_filter import RequestFilter
from includes.utils.utils import _resolve_request_getter, set_response


@dataclass
class PaginatorRecord:
    records: list
    pagination: list
    total_count: int


class NewQueryPaginator:

    @classmethod
    async def _global_filter(cls, type: Optional[str] = None, model: Any = None):
        conditions = []

        global_search = _resolve_request_getter(type, "where")
        if inspect.isawaitable(global_search):
            global_search = await global_search

        if global_search is None:
            return conditions

        for item in str(global_search).split("/"):
            name, sep, value = item.partition("=")
            name = name.strip()
            value = value.strip()

            if not sep or not name or not value:
                continue

            column = getattr(model, name, None)
            if column is not None:
                conditions.append(column == value)

        return conditions

    @classmethod
    def get_order_by(cls, model: Any, otherinfo: dict, orders: Any = None):
        order_asc = otherinfo.get("asc")
        order_desc = otherinfo.get("desc")

        if order_asc:
            column = getattr(model, order_asc, None)
            if column is not None:
                return asc(column)

        if order_desc:
            column = getattr(model, order_desc, None)
            if column is not None:
                return desc(column)

        if orders is not None:
            column = getattr(model, "timestamp", None)
            if column is not None:
                return desc(column)

            column = getattr(model, "id", None)
            if column is not None:
                return desc(column)

        return None

    @classmethod
    async def paginate(
        cls,
        limit: int = 10,
        model: Any = None,
        query: Any = None,
        types: Optional[str] = "query",
        columns: Optional[dict] = None,
        transform: Optional[Callable] = None,
        orders: Any = None,
        search_columns: Optional[list] = None,
        db: Any | None = None,
        **otherinfo,
    ) -> PaginatorRecord:
        otherinfo = otherinfo.copy() if otherinfo else {}

        # 2. Apply Global Search Filter
        global_conditions = await cls._global_filter(type=types, model=model)
        if global_conditions and hasattr(query, "where"):
            query = query.where(*global_conditions)

        # 3. Apply Dynamic Request Filters
        if model is not None:
            query = await RequestFilter.apply_request_filters(
                model=model,
                query=query,
                columns=columns,
                request_type=types or "query",
                search_columns=search_columns,
            )

        # 4. Resolve Order By Clause
        order_by = cls.get_order_by(
            model=model,
            otherinfo=otherinfo,
            orders=orders,
        )

        # 5. Execute Core Pagination
        records, pagination, total_count = await Pagination.get_paginate(
            limit=limit,
            query=query,
            order_by=order_by,
            request_type=types,
            transform=transform,
            db=db,
        )

        # Context updates
        set_response("results", total_count)
        set_response("paginator", pagination)

        return PaginatorRecord(
            records=records, pagination=pagination, total_count=total_count
        )
