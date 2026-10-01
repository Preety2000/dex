import inspect
from typing import Literal

from sqlalchemy import String, Text, and_, or_

from includes.db.models.db_exam import JsonList
from includes.utils.utils import _resolve_request_getter

RequestType = Literal["query", "api", "referer"]


class RequestFilter:
    """
    Fast request-based SQLAlchemy filtering.
    Request:

        ?category=JEE
        ?name=NEET|JEE
        ?where=category=JEE/name=test
        ?gs=rahul
        ?asc=date
        ?desc=name
    """

    def __init__(
        self,
        *,
        model,
        request_type: RequestType = "query",
        columns: dict[str, str] | None = None,
        search_columns: list[str] | None = None,
    ):
        if columns is not None and not isinstance(columns, dict):
            raise TypeError("columns must be a dict")

        if search_columns is not None and not isinstance(
            search_columns, (list, tuple, set)
        ):
            raise TypeError("search_columns must be a list, tuple or set")

        self.model = model

        self.columns = self._build_columns(columns)
        self._get_value = _resolve_request_getter(request_type)
        self.search_columns = self._build_search_columns(search_columns)

    def _build_columns(self, columns: dict[str, str] | None) -> dict:
        table_columns = {column.name: column for column in self.model.__table__.columns}

        if not columns:
            return table_columns

        for column_name, api_name in columns.items():
            column = table_columns.pop(column_name, None)

            if column is not None:
                table_columns[api_name] = column

        return table_columns

    def _build_search_columns(self, search_columns: list[str] | None) -> dict:

        if search_columns is not None:
            result = {}

            for name in search_columns:
                column = self.columns.get(name)

                if column is not None:
                    result[name] = column

            return result

        result = {}

        for name, column in self.columns.items():
            if isinstance(column.type, (String, Text)):
                result[name] = column

        return result

    async def _get_request_value(self, name: str):
        value = self._get_value(name)

        if inspect.isawaitable(value):
            value = await value

        return value

    @staticmethod
    def _split_values(value):
        if value is None:
            return []

        return [item.strip() for item in str(value).split("|") if item.strip()]

    @staticmethod
    def _parse_search_items(value):
        if not value:
            return

        for item in str(value).split("/"):
            name, separator, item_value = item.partition("=")

            name = name.strip()
            item_value = item_value.strip()

            if not name:
                continue

            yield name, item_value, separator

    async def _apply_column_filter(self, query, name, column):
        value = await self._get_request_value(name)

        if value is None:
            return query

        values = self._split_values(value)

        if not values:
            return query

        # JSON/List column
        if isinstance(column.type, JsonList):
            conditions = [column.cast(Text).ilike(f"%{item}%") for item in values]

            return query.filter(or_(*conditions))

        return query.filter(column.in_(values))

    async def _global_filter(self):
        conditions = []

        value = await self._get_request_value("where")

        for name, item_value, separator in self._parse_search_items(value):
            if not separator or not item_value:
                continue

            item_value = {
                "draft": "Draft",
                "publish": "Publish",
            }.get(item_value, item_value)

            column = self.columns.get(name)
            if column is not None:
                conditions.append(column == item_value)

        return conditions

    async def _global_search(self):
        conditions = []

        value = await self._get_request_value("gs")

        if not value:
            return conditions

        for name, item_value, separator in self._parse_search_items(value):
            # gs=name=Rahul
            # Search only the specified column.
            if separator and item_value:
                column = self.columns.get(name)

                if column is None:
                    continue

                conditions.append(column.ilike(f"%{item_value}%"))

                continue

            # gs=Rahul
            # Search across configured text columns.
            if name:
                for column in self.search_columns.values():
                    conditions.append(column.ilike(f"%{name}%"))

        return conditions

    async def _apply_order(self, query):
        asc = await self._get_request_value("asc")
        desc = await self._get_request_value("desc")
        order = await self._get_request_value("order")

        for name, value, separator in self._parse_search_items(order):
            if separator and value:
                if name == "asc":
                    asc = value
                elif name == "desc":
                    desc = value

        value, direction = (asc, "asc") if asc else (desc, "desc")

        if value:
            column = self.columns.get(str(value).strip())
            if column is not None:
                return query.order_by(getattr(column, direction)())

        return query

    async def apply(self, *, query):

        # WHERE
        conditions = await self._global_filter()

        if conditions:
            query = query.filter(and_(*conditions))

        # GLOBAL SEARCH
        conditions = await self._global_search()

        if conditions:
            query = query.filter(or_(*conditions))

        # COLUMN FILTERS
        for name, column in self.columns.items():
            query = await self._apply_column_filter(query, name, column)

        # ORDER
        query = await self._apply_order(query)

        return query

    @classmethod
    async def apply_request_filters(
        cls,
        *,
        model,
        query,
        request_type: RequestType = "query",
        columns: dict[str, str] | None = None,
        search_columns: list[str] | None = None,
    ):
        filter_method = cls(
            model=model,
            columns=columns,
            request_type=request_type,
            search_columns=search_columns,
        )

        return await filter_method.apply(query=query)
