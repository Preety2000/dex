from sqlalchemy import select

from includes.core.globals.entry import app_context
from includes.database.connection import active_secondary_db
from includes.database.models.secondary import Terms
from includes.database.dataclass.dataclass import _Terms, serialize
from includes.schemas.cache.dataclass import _TermsCache


TermsCacheData = _TermsCache()
CACHE_BY_SUBJECT = {}


class TermsCache:

    @staticmethod
    def _cache(record: _Terms) -> _Terms:
        if isinstance(record, Terms):
            record = _Terms(**serialize(record))

        TermsCacheData.ById[record.id] = record
        TermsCacheData.BySlug[record.slug] = record.id
        TermsCacheData.ByName[record.name] = record.id

        return record

    @staticmethod
    def _cache_remove():
        global TermsCacheData, CACHE_BY_SUBJECT

        TermsCacheData = _TermsCache()
        CACHE_BY_SUBJECT = {}

    @staticmethod
    async def get_by_id(id: int) -> _Terms:
        record = TermsCacheData.ById.get(id)

        if record:
            return record
        
        db = await active_secondary_db()

        record = db.execute(
            select(Terms).where(
                Terms.id == id
            )
        ).scalar_one_or_none()

        if not record:
            return None

        return TermsCache._cache(
            _Terms(**serialize(record))
        )

    @staticmethod
    async def get_by_slug(slug: str) -> _Terms:
        cached_id = TermsCacheData.BySlug.get(slug)

        if cached_id:
            return await TermsCache.get_by_id(cached_id)
        
        db = await active_secondary_db()
        record = db.execute(
            select(Terms).where(
                Terms.slug == slug
            )
        ).scalar_one_or_none()

        if not record:
            return None

        return TermsCache._cache(
            _Terms(**serialize(record))
        )

    @staticmethod
    async def get_by_name(name: str) -> _Terms:
        cached_id = TermsCacheData.ByName.get(name)

        if cached_id:
            return await TermsCache.get_by_id(cached_id)

        db = await active_secondary_db()
        record = db.execute(
            select(Terms).where(
                Terms.name == name
            )
        ).scalar_one_or_none()

        if not record:
            return None

        return TermsCache._cache(
            _Terms(**serialize(record))
        )

    @staticmethod
    async def get_by_subject(subject_id: int) -> list[_Terms]:
        global CACHE_BY_SUBJECT

        data = CACHE_BY_SUBJECT.get(subject_id)

        if data is None:
            db = await active_secondary_db()
            records = db.execute(
                select(Terms).where(
                    Terms.subject_id == subject_id
                )
            ).scalars().all()

            data = [
                TermsCache._cache(
                    _Terms(**serialize(record))
                )
                for record in records
            ]

            CACHE_BY_SUBJECT[subject_id] = data

        return data

    @staticmethod
    async def get_all() -> list[_Terms]:
        if TermsCacheData.allList:
            return TermsCacheData.allList

        db = await active_secondary_db()
        records = db.execute(
            select(Terms).order_by(
                Terms.name
            )
        ).scalars().all()

        TermsCacheData.allList = [
            TermsCache._cache(
                _Terms(**serialize(record))
            )
            for record in records
        ]

        return TermsCacheData.allList

    @staticmethod
    async def get_many(id_list: list[int]):
        records = []
        missing = []

        for qid in id_list or []:
            record = TermsCacheData.ById.get(qid)

            if record:
                records.append(record)
            else:
                missing.append(qid)

        if missing:
            db = await active_secondary_db()
            db_records = db.execute(
                select(Terms).where(
                    Terms.id.in_(missing)
                )
            ).scalars().all()

            records.extend(
                TermsCache._cache(
                    _Terms(**serialize(record))
                )
                for record in db_records
            )

        return records
