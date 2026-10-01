from includes.core.config import secondary_database
from includes.db.models.secondary import Suggestion
from includes.db.dataclass import _Suggestion
from includes.schemas.cache.dataclass import _SuggestionCache

SuggestionCacheData = _SuggestionCache()


class SuggestionCache:

    @staticmethod
    def _cache(record: _Suggestion) -> _Suggestion:
        SuggestionCacheData.ById[record.id] = record

        return record

    @staticmethod
    async def get(id: int) -> _Suggestion:
        record = SuggestionCacheData.ById.get(id)
        if record:
            return record

        with secondary_database() as db:
            record = db.query(Suggestion).filter(Suggestion.id == id).first()
            if not record:
                return None

            return SuggestionCache._cache(record.to_dataclass())

    @staticmethod
    async def get_all():

        if SuggestionCacheData.allList:
            return SuggestionCacheData.allList

        with secondary_database() as db:
            SuggestionCacheData.allList = [
                SuggestionCache._cache(record.to_dataclass())
                for record in db.query(Suggestion).all()
            ]
            return SuggestionCacheData.allList

        return []

    @staticmethod
    async def get_many(id_list: list[int]):
        records = []
        missing = []

        for qid in id_list or []:
            record = SuggestionCacheData.ById.get(qid)
            records.append(record) if record else missing.append(qid)

        if missing:
            with secondary_database() as db:
                records.extend(
                    SuggestionCache._cache(r.to_dataclass())
                    for r in db.query(Suggestion)
                    .filter(Suggestion.id.in_(missing))
                    .all()
                )

        return records
