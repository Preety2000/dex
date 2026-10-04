from sqlalchemy import func, select

from includes.core.globals.entry import app_context
from includes.database.models.owner import Subject
from includes.database.dataclass.dataclass import _Subject
from includes.database.models.secondary import QuizQuestion, QuizRelationships, Terms
from includes.schemas.cache.dataclass import _SubjectCache
from includes.database.connection import active_primary_db

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

        db = await active_primary_db()
        stmt = select(Subject).where(Subject.id == id)
        record = db.execute(stmt).scalar_one_or_none()

        if not record:
            return None

        return SubjectCache._cache(record.to_dataclass())

    @staticmethod
    async def get_by_slug(slug: str) -> _Subject:
        if SubjectCacheData.BySlug.get(slug):
            return await SubjectCache.get_by_id(SubjectCacheData.BySlug[slug])

        stmt = select(Subject).where(Subject.slug == slug)
        db = await active_primary_db()
        record = db.execute(stmt).scalar_one_or_none()

        if not record:
            return None

        return SubjectCache._cache(record.to_dataclass())

    @staticmethod
    async def get_by_name(name: str) -> _Subject:
        if SubjectCacheData.ByName.get(name):
            return await SubjectCache.get_by_id(SubjectCacheData.ByName[name])

        stmt = select(Subject).where(Subject.name == name)
        db = await active_primary_db()
        record = db.execute(stmt).scalar_one_or_none()

        if not record:
            return None

        return SubjectCache._cache(record.to_dataclass())

    @staticmethod
    async def get_all():
        db = await active_primary_db()
        count = db.execute(select(func.count()).select_from(Subject)).scalar_one()
        
        if len(SubjectCacheData.ById) == count:
            return list(SubjectCacheData.ById.values())
            
        SubjectCacheData.ById.clear()
        SubjectCacheData.BySlug.clear()
        SubjectCacheData.ByName.clear()

        records = db.execute(select(Subject).order_by(Subject.name)).scalars().all()
        return [
            SubjectCache._cache(record.to_dataclass()) 
            for record in records
        ]

    @staticmethod
    async def get_mcqlist_count(category: str, subject=None):

        ids = [
            record.id
            for record in await SubjectCache.get_all()
            if not subject or record.name == subject
        ]

        stmt = (
            select(
                Terms.subject_id,
                func.count(QuizQuestion.id),
            )
            .join(
                QuizRelationships,
                QuizRelationships.terms_id == Terms.id,
            )
            .join(
                QuizQuestion,
                QuizQuestion.id == QuizRelationships.quiz_id,
            )
            .where(Terms.subject_id.in_(ids))
        )

        if category != "default":
            stmt = stmt.where((Terms.slug == category) | (Terms.name == category))

        stmt = stmt.group_by(Terms.subject_id)

        rows = app_context.secondary_session.execute(stmt).all()
        return dict(rows)

    @staticmethod
    async def get_many(id_list: list[int]):
        records = []
        missing = []

        for qid in id_list or []:
            record = SubjectCacheData.ById.get(qid)

            if record:
                records.append(record)
            else:
                missing.append(qid)

        if missing:
            stmt = select(Subject).where(Subject.id.in_(missing))
            db = await active_primary_db()
            db_records = db.execute(stmt).scalars().all()

            records.extend(
                SubjectCache._cache(record.to_dataclass()) for record in db_records
            )

        return records
