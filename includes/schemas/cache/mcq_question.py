from sqlalchemy import select

from includes.database.dataclass.dataclass import _QuizQuestion
from includes.schemas.cache.dataclass import QuizQuesCache
from includes.database.connection import active_secondary_db
from includes.database.models.secondary import (
    QuizQuestion,
    QuizRelationships,
)


QuizQuestionCacheData = QuizQuesCache()


class QuizQuestionCache:

    @staticmethod
    async def _cache(record: QuizQuestion) -> _QuizQuestion:
        _record = await record.to_dict()

        QuizQuestionCacheData.ById[record.id] = _record

        return _record

    @staticmethod
    async def get(id: int) -> _QuizQuestion:
        record = QuizQuestionCacheData.ById.get(id)

        if record:
            return record

        db = await active_secondary_db()

        stmt = (
            select(QuizQuestion)
            .where(QuizQuestion.id == id)
            .limit(1)
        )

        result = db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        return await QuizQuestionCache._cache(record)

    @staticmethod
    async def get_many(id_list: list[int]):
        records = []
        missing = []

        for qid in id_list or []:
            record = QuizQuestionCacheData.ById.get(qid)

            if record:
                records.append(record)
            else:
                missing.append(qid)

        if not missing:
            return records

        db = await active_secondary_db()

        stmt = (
            select(QuizQuestion)
            .where(QuizQuestion.id.in_(missing))
        )

        result = db.execute(stmt)
        db_records = result.scalars().all()

        # Cache + preserve requested order
        cached_records = {}

        for record in db_records:
            cached_records[record.id] = (
                await QuizQuestionCache._cache(record)
            )

        records.extend(
            cached_records[qid]
            for qid in missing
            if qid in cached_records
        )

        return records

    @staticmethod
    async def get_first_by_terms_id(
        terms_id: int,
    ):
        cached_id = QuizQuestionCacheData.ByTermId.get(terms_id)

        if cached_id:
            return await QuizQuestionCache.get(cached_id)

        db = await active_secondary_db()

        stmt = (
            select(QuizQuestion)
            .join(
                QuizRelationships,
                QuizRelationships.quiz_id == QuizQuestion.id,
            )
            .where(
                QuizRelationships.terms_id == terms_id
            )
            .limit(1)
        )

        result = db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        QuizQuestionCacheData.ByTermId[terms_id] = record.id

        return await QuizQuestionCache._cache(record)
