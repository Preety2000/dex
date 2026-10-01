import calendar
import json
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, Text, TypeDecorator
from datetime import date, datetime, tzinfo
from sqlalchemy.types import TypeDecorator, Text

# New Delhi / IST timezone define karein
IST = ZoneInfo("Asia/Kolkata")


class JsonList(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []

        try:
            data = json.loads(value)

            if isinstance(data, (list, dict)):
                return data

            return []
        except Exception:
            if isinstance(value, str):
                return value.split(",")

            return []


def to_datetime(
    value: int | float | str | datetime | None = None, tz: tzinfo = IST
) -> datetime:
    if value is None or value == "":
        return datetime.now(tz)

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=tz)

        return value.astimezone(tz)

    if isinstance(value, (int, float)):
        if value > 1e11:
            value = value / 1000.0
        return datetime.fromtimestamp(value, tz=tz)

    if isinstance(value, str):
        if value.isdigit():
            ts = int(value)
            if ts > 1e11:
                ts = ts / 1000.0
            return datetime.fromtimestamp(ts, tz=tz)

        clean_value = value.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(clean_value)
        except ValueError:
            dt = datetime.strptime(value.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        if dt.tzinfo is None:
            return dt.replace(tzinfo=tz)
        return dt.astimezone(tz)

    raise TypeError(f"Unsupported type for to_datetime: {type(value)}")


# class TimeStamp(TypeDecorator):
#     """SQLAlchemy Custom Type storing ISO formatted strings in DB and returning 13-digit Millisecond Unix Timestamps to Python.
#     """

#     impl = DateTime(timezone=True)
#     cache_ok = True

#     def process_bind_param(self, value, dialect):
#         if value is None or value == "":
#             return None
#         return to_datetime(value, IST).strftime("%Y-%m-%dT%H:%M:%S%z")

#     def process_result_value(self, value, dialect):
#         if not value:
#             return None
#         return int(to_datetime(value, IST).timestamp() * 1000)

#     @classmethod
#     def now_timestamp(cls) -> int:
#         return int(datetime.now(IST).timestamp() * 1000)

#     @classmethod
#     def now_iso(cls) -> str:
#         return datetime.now(IST).strftime("%Y-%m-%dT%H:%M:%S%z")

#     @classmethod
#     def timestamp(cls, value: int | str | datetime | None = None) -> str:
#         return to_datetime(value, IST)

#     @classmethod
#     def format_ts(cls, ts: int | None, fmt: str = "%Y-%m-%dT%H:%M:%S%z") -> str:
#         if ts is None:
#             return None

#         return to_datetime(ts, IST).strftime(fmt)


#     @classmethod
#     def format_ms(cls, value: int | str | datetime | None = None) -> int:
#         return int(to_datetime(value, IST).timestamp() * 1000)


#     @staticmethod
#     def _get_day_range(target_date: date | None = None) -> tuple[int, int]:
#         today = target_date if target_date is not None else date.today()
#         start_dt = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=IST)
#         end_dt = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=IST)

#         return int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000)

#     @staticmethod
#     def _get_month_range(year: int | None = None, month: int | None = None) -> tuple[int, int]:
#         today = date.today()
#         y = year if year is not None else today.year
#         m = month if month is not None else today.month
#         start_dt = datetime(y, m, 1, 0, 0, 0, tzinfo=IST)
#         _, last_day = calendar.monthrange(y, m)
#         end_dt = datetime(y, m, last_day, 23, 59, 59, tzinfo=IST)

#         return int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000)

#     @staticmethod
#     def _get_year_range(year: int | None = None) -> tuple[int, int]:
#         today = date.today()
#         y = year if year is not None else today.year

#         start_dt = datetime(y, 1, 1, 0, 0, 0, tzinfo=IST)
#         end_dt = datetime(y, 12, 31, 23, 59, 59, tzinfo=IST)

#         return int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000)

#     @classmethod
#     def get_range(
#         cls,
#         start_year: int | None = None,
#         end_year: int | None = None,
#         start_month: int | None = None,
#         end_month: int | None = None,
#         start_week: int | None = None,
#         end_week: int | None = None,
#         start_hour: int | None = None,
#         end_hour: int | None = None,
#     ) -> tuple[str, str]:
#         now = datetime.now(IST)

#         # 1. Determine Years
#         sy = start_year if start_year is not None else now.year
#         ey = end_year if end_year is not None else sy

#         # 2. Determine Months
#         sm = start_month if start_month is not None else 1
#         em = end_month if end_month is not None else (12 if end_month is None and start_month is None else sm)

#         # 3. Determine Hours
#         sh = start_hour if start_hour is not None else 0
#         eh = end_hour if end_hour is not None else 23

#         # Calculate Start Date
#         start_dt = datetime(sy, sm, 1, sh, 0, 0, tzinfo=IST)
#         if start_week is not None:
#             # Shift to specific ISO week
#             start_dt = datetime.fromisocalendar(sy, start_week, 1).replace(hour=sh, minute=0, second=0, tzinfo=IST)

#         # Calculate End Date
#         if end_week is not None:
#             end_dt = datetime.fromisocalendar(ey, end_week, 7).replace(hour=eh, minute=59, second=59, tzinfo=IST)
#         else:
#             _, last_day = calendar.monthrange(ey, em)
#             end_dt = datetime(ey, em, last_day, eh, 59, 59, tzinfo=IST)

#         return (start_dt.strftime("%Y-%m-%dT%H:%M:%S%z"), end_dt.strftime("%Y-%m-%dT%H:%M:%S%z"))

#     @classmethod
#     def get_period(
#         cls,
#         year: int | None = None,
#         month: int | None = None,
#         week: int | None = None,
#         hour: int | None = None,
#     ) -> tuple[str, str]:
#         now = datetime.now(IST)
#         target_year = year if year is not None else now.year

#         # Case 1: Specific Hour
#         if hour is not None:
#             target_month = month if month is not None else now.month
#             target_day = now.day
#             start_dt = datetime(target_year, target_month, target_day, hour, 0, 0, tzinfo=IST)
#             end_dt = datetime(target_year, target_month, target_day, hour, 59, 59, tzinfo=IST)

#         # Case 2: Specific ISO Week Number
#         elif week is not None:
#             start_dt = datetime.fromisocalendar(target_year, week, 1).replace(hour=0, minute=0, second=0, tzinfo=IST)
#             end_dt = datetime.fromisocalendar(target_year, week, 7).replace(hour=23, minute=59, second=59, tzinfo=IST)

#         # Case 3: Specific Month
#         elif month is not None:
#             _, last_day = calendar.monthrange(target_year, month)
#             start_dt = datetime(target_year, month, 1, 0, 0, 0, tzinfo=IST)
#             end_dt = datetime(target_year, month, last_day, 23, 59, 59, tzinfo=IST)

#         # Case 4: Full Year
#         else:
#             start_dt = datetime(target_year, 1, 1, 0, 0, 0, tzinfo=IST)
#             end_dt = datetime(target_year, 12, 31, 23, 59, 59, tzinfo=IST)

#         return (start_dt.strftime("%Y-%m-%dT%H:%M:%S%z"), end_dt.strftime("%Y-%m-%dT%H:%M:%S%z"))


class TimeStamp(TypeDecorator):
    """
    SQLAlchemy custom DateTime type.

    Database:
        Stores Python datetime through SQLAlchemy DateTime.

    Python:
        Returns 13-digit Unix timestamp in milliseconds.

    Input:
        Accepts:
        - None
        - ""
        - datetime
        - date
        - int / float (milliseconds timestamp)
        - ISO datetime string
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    # ==========================================================
    # BIND: Python -> Database
    # ==========================================================

    def process_bind_param(self, value, dialect):
        if value is None or value == "":
            return None

        # Already datetime
        if isinstance(value, datetime):
            dt = value

        # Date
        elif isinstance(value, date):
            dt = datetime(
                value.year,
                value.month,
                value.day,
            )

        # Unix milliseconds
        elif isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(
                value / 1000,
                tz=IST,
            )

        # String
        elif isinstance(value, str):
            dt = to_datetime(value, IST)

        else:
            raise TypeError(f"Unsupported TimeStamp value: " f"{type(value).__name__}")

        # Make sure timezone exists
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST)

        # IMPORTANT:
        # Return datetime, NOT string.
        return dt

    # ==========================================================
    # RESULT: Database -> Python
    # ==========================================================

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        # SQLite/PostgreSQL should normally return datetime
        if isinstance(value, datetime):
            dt = value

        else:
            dt = to_datetime(value, IST)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST)

        return int(dt.timestamp() * 1000)

    # ==========================================================
    # CURRENT TIMESTAMP
    # ==========================================================

    @classmethod
    def now_timestamp(cls) -> int:
        """
        Current IST time as 13-digit milliseconds.
        """
        return int(datetime.now(IST).timestamp() * 1000)

    @classmethod
    def now_datetime(cls) -> datetime:
        """
        Current IST datetime.
        Use this for SQLAlchemy DateTime values.
        """
        return datetime.now(IST)

    @classmethod
    def now_iso(cls) -> str:
        """
        Current IST time as ISO string.
        """
        return datetime.now(IST).strftime("%Y-%m-%dT%H:%M:%S%z")

    # ==========================================================
    # CONVERT TO DATETIME
    # ==========================================================

    @classmethod
    def timestamp(
        cls,
        value: int | str | datetime | date | None = None,
    ) -> datetime | None:

        if value is None:
            return None

        return to_datetime(
            value,
            IST,
        )

    # ==========================================================
    # FORMAT TIMESTAMP
    # ==========================================================

    @classmethod
    def format_ts(
        cls,
        ts: int | None,
        fmt: str = "%Y-%m-%dT%H:%M:%S%z",
    ) -> str | None:

        if ts is None:
            return None

        return to_datetime(
            ts,
            IST,
        ).strftime(fmt)

    # ==========================================================
    # FORMAT MILLISECOND TIMESTAMP
    # ==========================================================

    @classmethod
    def format_ms(
        cls,
        value: int | str | datetime | date | None = None,
    ) -> int | None:

        if value is None:
            return None

        return int(
            to_datetime(
                value,
                IST,
            ).timestamp()
            * 1000
        )

    # ==========================================================
    # DAY RANGE
    # ==========================================================

    @staticmethod
    def _get_day_range(
        target_date: date | None = None,
    ) -> tuple[int, int]:

        today = target_date if target_date is not None else datetime.now(IST).date()

        start_dt = datetime(
            today.year,
            today.month,
            today.day,
            0,
            0,
            0,
            tzinfo=IST,
        )

        end_dt = datetime(
            today.year,
            today.month,
            today.day,
            23,
            59,
            59,
            tzinfo=IST,
        )

        return (
            int(start_dt.timestamp() * 1000),
            int(end_dt.timestamp() * 1000),
        )

    # ==========================================================
    # MONTH RANGE
    # ==========================================================

    @staticmethod
    def _get_month_range(
        year: int | None = None,
        month: int | None = None,
    ) -> tuple[int, int]:

        today = datetime.now(IST)

        y = year if year is not None else today.year

        m = month if month is not None else today.month

        start_dt = datetime(
            y,
            m,
            1,
            0,
            0,
            0,
            tzinfo=IST,
        )

        _, last_day = calendar.monthrange(
            y,
            m,
        )

        end_dt = datetime(
            y,
            m,
            last_day,
            23,
            59,
            59,
            tzinfo=IST,
        )

        return (
            int(start_dt.timestamp() * 1000),
            int(end_dt.timestamp() * 1000),
        )

    # ==========================================================
    # YEAR RANGE
    # ==========================================================

    @staticmethod
    def _get_year_range(
        year: int | None = None,
    ) -> tuple[int, int]:

        today = datetime.now(IST)

        y = year if year is not None else today.year

        start_dt = datetime(
            y,
            1,
            1,
            0,
            0,
            0,
            tzinfo=IST,
        )

        end_dt = datetime(
            y,
            12,
            31,
            23,
            59,
            59,
            tzinfo=IST,
        )

        return (
            int(start_dt.timestamp() * 1000),
            int(end_dt.timestamp() * 1000),
        )

    # ==========================================================
    # RANGE
    # ==========================================================

    @classmethod
    def get_range(
        cls,
        start_year: int | None = None,
        end_year: int | None = None,
        start_month: int | None = None,
        end_month: int | None = None,
        start_week: int | None = None,
        end_week: int | None = None,
        start_hour: int | None = None,
        end_hour: int | None = None,
    ) -> tuple[str, str]:

        now = datetime.now(IST)

        # ------------------------------------------------------
        # Years
        # ------------------------------------------------------

        sy = start_year if start_year is not None else now.year

        ey = end_year if end_year is not None else sy

        # ------------------------------------------------------
        # Months
        # ------------------------------------------------------

        sm = start_month if start_month is not None else 1

        if end_month is not None:
            em = end_month
        elif start_month is not None:
            em = start_month
        else:
            em = 12

        # ------------------------------------------------------
        # Hours
        # ------------------------------------------------------

        sh = start_hour if start_hour is not None else 0

        eh = end_hour if end_hour is not None else 23

        # ------------------------------------------------------
        # Start
        # ------------------------------------------------------

        start_dt = datetime(
            sy,
            sm,
            1,
            sh,
            0,
            0,
            tzinfo=IST,
        )

        if start_week is not None:

            start_dt = datetime.fromisocalendar(
                sy,
                start_week,
                1,
            ).replace(
                hour=sh,
                minute=0,
                second=0,
                microsecond=0,
                tzinfo=IST,
            )

        # ------------------------------------------------------
        # End
        # ------------------------------------------------------

        if end_week is not None:

            end_dt = datetime.fromisocalendar(
                ey,
                end_week,
                7,
            ).replace(
                hour=eh,
                minute=59,
                second=59,
                microsecond=999999,
                tzinfo=IST,
            )

        else:

            _, last_day = calendar.monthrange(
                ey,
                em,
            )

            end_dt = datetime(
                ey,
                em,
                last_day,
                eh,
                59,
                59,
                tzinfo=IST,
            )

        return (
            start_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
            end_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
        )

    # ==========================================================
    # PERIOD
    # ==========================================================

    @classmethod
    def get_period(
        cls,
        year: int | None = None,
        month: int | None = None,
        week: int | None = None,
        hour: int | None = None,
    ) -> tuple[str, str]:

        now = datetime.now(IST)

        target_year = year if year is not None else now.year

        # ------------------------------------------------------
        # Specific Hour
        # ------------------------------------------------------

        if hour is not None:

            target_month = month if month is not None else now.month

            target_day = now.day

            start_dt = datetime(
                target_year,
                target_month,
                target_day,
                hour,
                0,
                0,
                tzinfo=IST,
            )

            end_dt = datetime(
                target_year,
                target_month,
                target_day,
                hour,
                59,
                59,
                tzinfo=IST,
            )

        # ------------------------------------------------------
        # Specific ISO Week
        # ------------------------------------------------------

        elif week is not None:

            start_dt = datetime.fromisocalendar(
                target_year,
                week,
                1,
            ).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
                tzinfo=IST,
            )

            end_dt = datetime.fromisocalendar(
                target_year,
                week,
                7,
            ).replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
                tzinfo=IST,
            )

        # ------------------------------------------------------
        # Specific Month
        # ------------------------------------------------------

        elif month is not None:

            _, last_day = calendar.monthrange(
                target_year,
                month,
            )

            start_dt = datetime(
                target_year,
                month,
                1,
                0,
                0,
                0,
                tzinfo=IST,
            )

            end_dt = datetime(
                target_year,
                month,
                last_day,
                23,
                59,
                59,
                tzinfo=IST,
            )

        # ------------------------------------------------------
        # Full Year
        # ------------------------------------------------------

        else:

            start_dt = datetime(
                target_year,
                1,
                1,
                0,
                0,
                0,
                tzinfo=IST,
            )

            end_dt = datetime(
                target_year,
                12,
                31,
                23,
                59,
                59,
                tzinfo=IST,
            )

        return (
            start_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
            end_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
        )
