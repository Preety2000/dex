import time
from sqlalchemy import select
from typing import Any,  Iterable

from includes.core.globals.coreutils import format_view_count
from includes.database.connection import active_secondary_db, get_contry
from includes.database.models.secondary import ArticleView, QuizView



VIEW_CACHE: dict[str, dict[int, dict[str, Any]]] = {
    "article": {},
    "practice": {},
}

class MetricsManager:
    """Manages in-memory buffering and periodic database flushing
    for view counts and rankings across entities.
    """

    def __init__(self, flush_interval_minutes: int = 5):
        self.models = None
        self.flush_ms = flush_interval_minutes * 60 * 1000


    @staticmethod
    def _now_ms() -> int:
        return int(time.time() * 1000)

    def _is_expired(self, updated_ms: int) -> bool:
        return (self._now_ms() - updated_ms) >= self.flush_ms

    @staticmethod
    async def track_views(item_type: str, id: int, update:bool=True) -> int:
        """Increment views in memory and periodically flush to DB."""
        country = await get_contry()
        type_cache = VIEW_CACHE.get(item_type)
        manager = MetricsManager(flush_interval_minutes=1)

        if type_cache is None:
            raise ValueError(f"Unsupported item_type: {item_type}")

        if item_type == "article":
            manager.models = ArticleView
        
        elif item_type == "practice":
            manager.models = QuizView
            
        if id not in type_cache:
            type_cache[id] = {
                "country": country, 
                "views": await manager._fetch_views(id),
                "timestamp": manager._now_ms(),
            }

        # Request count increment
        if update is True:
            type_cache[id]["views"] += 1

        type_cache[id]["country"] = country

        # Periodic flush execution
        if manager._is_expired(type_cache[id]["timestamp"]):
            cached_views = type_cache[id]["views"]
            target_country = type_cache[id]["country"]
            synced_views = await manager._sync_views( id, cached_views, target_country)

            type_cache[id] = {
                "views": synced_views,
                "country": target_country,
                "timestamp": manager._now_ms(),
            }

        return type_cache[id]["views"]

    # Views
    async def _fetch_views(self, id: int) -> int:
        db_session = await active_secondary_db()
        stmt = select(self.models.view_count).where(self.models.id == id)
        result = db_session.execute(stmt)
        val = result.scalar_one_or_none()

        return val if val is not None else 0

    async def _sync_views(self, id: int, views: int=1, country: str=None) -> int:
        db_session = await active_secondary_db()

        stmt = select(self.models).where(self.models.id == id)
        result = db_session.execute(stmt)
        record = result.scalar_one_or_none()

        if record is None:
            new_record = self.models(id=id, view_count=views)
            db_session.add(new_record)
        else:
            record.view_count = views

        db_session.commit()
        return views

    # Ranking
    async def _persist_rank(self, id: int, rank_value: int) -> int:
        return rank_value

    @classmethod
    async def article_metrics(cls, id: int, options: Iterable[str], servic=None) -> dict[str, Any]:
        result: dict[str, Any] = {}
        options_set = set(options)

        if "rank" in options_set and servic:
            result["rank"] = await servic.get_article_rank(id)

        if "views" in options_set:
            total_views = await cls.track_views("article", id)
            result["views"] = format_view_count(total_views)

        return result

    @classmethod
    async def practice_metrics(cls, mcq_id: int, options: Iterable[str], servic=None) -> dict[str, Any]:
        result: dict[str, Any] = {}
        options_set = set(options)

        if "views" in options_set:
            total_views = await cls.track_views("practice", mcq_id)
            result["views"] = format_view_count(total_views)

        return result

    @classmethod
    async def get_article_view(cls, id:int):
        return await cls.track_views("article", id, False)

