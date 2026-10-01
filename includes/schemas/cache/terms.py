from includes.core.globals.entry import app_context
from includes.db.models.secondary import Terms
from includes.db.dataclass import _Terms, serialize
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
        global CACHE_BY_SUBJECT
        TermsCacheData = _TermsCache()
        TermsCacheData.allList = None
        CACHE_BY_SUBJECT = {}

    @staticmethod
    async def get_by_id(id: int) -> _Terms:
        record = TermsCacheData.ById.get(id)
        if record:
            return record

        record = app_context.db.query(Terms).filter(Terms.id == id).first()
        if not record:
            return None
        return TermsCache._cache(_Terms(**serialize(record)))

    @staticmethod
    async def get_by_slug(slug: int) -> _Terms:
        if TermsCacheData.BySlug.get(slug):
            return await TermsCache.get_by_id(TermsCacheData.BySlug[slug])

        record = app_context.db.query(Terms).filter(Terms.slug == slug).first()
        if not record:
            return None
        return TermsCache._cache(_Terms(**serialize(record)))

    @staticmethod
    async def get_by_name(name: int) -> _Terms:
        if TermsCacheData.ByName.get(name):
            return await TermsCache.get_by_id(TermsCacheData.ByName[name])

        record = app_context.db.query(Terms).filter(Terms.name == name).first()
        if not record:
            return None
        return TermsCache._cache(_Terms(**serialize(record)))

    @staticmethod
    async def get_by_subject(subject_id: int) -> _Terms:
        global CACHE_BY_SUBJECT
        data = CACHE_BY_SUBJECT.get(subject_id, None)
        if data is None:
            da_data = (
                app_context.db.query(Terms).filter(Terms.subject_id == subject_id).all()
            )
            data = [
                TermsCache._cache(_Terms(**serialize(record))) for record in da_data
            ]
            CACHE_BY_SUBJECT[subject_id] = data

        return data

    @staticmethod
    async def get_all():

        if TermsCacheData.allList:
            return TermsCacheData.allList

        TermsCacheData.allList = [
            TermsCache._cache(_Terms(**serialize(record)))
            for record in app_context.db.query(Terms).order_by(Terms.name).all()
        ]
        return TermsCacheData.allList

        return []

    @staticmethod
    async def get_many(id_list: list[int]):
        records = []
        missing = []

        for qid in id_list or []:
            record = TermsCacheData.ById.get(qid)
            records.append(record) if record else missing.append(qid)

        if missing:
            records.extend(
                TermsCache._cache(_Terms(**serialize(r)))
                for r in app_context.db.query(Terms).filter(Terms.id.in_(missing)).all()
            )

        return records
