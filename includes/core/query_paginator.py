from dataclasses import dataclass
import inspect
from typing import Any, Callable

from sqlalchemy import asc, desc, func

from includes.core.globals.entry import app_context
from includes.utils.utils import _resolve_request_getter, set_response
from includes.core.pagination import Pagination
from includes.core.request_filter import RequestFilter


@dataclass
class PaginatorRecord:
    records: list
    pagination: list
    total_count: int


class QueryPaginator:

    @classmethod
    async def _global_filter(cls, type: str | None = None, model: Any | None = None):
        conditions = []

        global_search = _resolve_request_getter(type, "where")
        if inspect.isawaitable(global_search):
            global_search = await global_search

        if global_search is None:
            return

        for item in global_search.split("/"):
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
        types: str | None = None,
        columns: dict | None = None,
        callback: Callable | None = None,
        transform: Callable | None = None,
        orders: Any = None,
        search_columns: list = None,
        **otherinfo,
    ) -> PaginatorRecord:
        otherinfo = otherinfo.copy() if otherinfo else {}

        if callable(callback):
            query = callback(query)
            if inspect.isawaitable(query):
                query = await query

        query = await RequestFilter.apply_request_filters(
            model=model,
            query=query,
            columns=columns,
            request_type=types,
            search_columns=search_columns,
        )

        order_by = cls.get_order_by(
            model=model,
            otherinfo=otherinfo,
            orders=orders,
        )

        records, pagination, total_count = await Pagination.get_paginate(
            limit=limit,
            query=query,
            order_by=order_by,
            request_type=types,
            transform=transform,
        )

        set_response("results", total_count)
        set_response("paginator", pagination)

        return PaginatorRecord(
            records=records, pagination=pagination, total_count=total_count
        )
