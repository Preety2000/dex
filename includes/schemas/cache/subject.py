from sqlalchemy import func
from includes.core.globals.entry import app_context
from includes.db.models.owner import Subject
from includes.db.dataclass import _Subject
from includes.db.models.secondary import QuizQuestion, QuizRelationships, Terms
from includes.schemas.cache.dataclass import _SubjectCache

SubjectCacheData = _SubjectCache()


class SubjectCache:

    @staticmethod
    def _cache(record: _Subject) -> _Subject:
        SubjectCacheData.ById[record.id] = record
        SubjectCacheData.BySlug[record.slug] = record.id
        SubjectCacheData.ByName[record.name] = record.id

        return record

    @staticmethod
    async def get_by_id(id: int) -> _Subject:
        record = SubjectCacheData.ById.get(id)
        if record:
            return record

        record = app_context.db.query(Subject).filter(Subject.id == id).first()
        if not record:
            return None
        return SubjectCache._cache(record.to_dataclass())

    @staticmethod
    async def get_by_slug(slug: int) -> _Subject:
        if SubjectCacheData.BySlug.get(slug):
            return await SubjectCache.get_by_id(SubjectCacheData.BySlug[slug])

        record = app_context.db.query(Subject).filter(Subject.slug == slug).first()
        if not record:
            return None
        return SubjectCache._cache(record.to_dataclass())

    @staticmethod
    async def get_by_name(name: int) -> _Subject:
        if SubjectCacheData.ByName.get(name):
            return await SubjectCache.get_by_id(SubjectCacheData.ByName[name])

        record = app_context.db.query(Subject).filter(Subject.name == name).first()
        if not record:
            return None
        return SubjectCache._cache(record.to_dataclass())

    @staticmethod
    async def get_all():

        if SubjectCacheData.allList:
            return SubjectCacheData.allList

        SubjectCacheData.allList = [
            SubjectCache._cache(record.to_dataclass())
            for record in app_context.db.query(Subject).order_by(Subject.name).all()
        ]
        return SubjectCacheData.allList

    @staticmethod
    async def get_mcqlist_count(category: str, subject=None):

        ids = [
            record.id
            for record in await SubjectCache.get_all()
            if not subject or record.name == subject
        ]

        query = (
            app_context.secondary_session.query(
                Terms.subject_id, func.count(QuizQuestion.id)
            )
            .join(QuizRelationships, QuizRelationships.terms_id == Terms.id)
            .join(QuizQuestion, QuizQuestion.id == QuizRelationships.quiz_id)
            .filter(Terms.subject_id.in_(ids))
        )

        if category != "default":
            query = query.filter((Terms.slug == category) | (Terms.name == category))
        query = query.group_by(Terms.subject_id).all()
        counts = dict(query)
        return counts

    @staticmethod
    async def get_many(id_list: list[int]):
        records = []
        missing = []

        for qid in id_list or []:
            record = SubjectCacheData.ById.get(qid)
            records.append(record) if record else missing.append(qid)

        if missing:
            records.extend(
                SubjectCache._cache(r.to_dataclass())
                for r in app_context.db.query(Subject)
                .filter(Subject.id.in_(missing))
                .all()
            )

        return records
