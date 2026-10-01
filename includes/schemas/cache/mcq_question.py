from includes.core.globals.entry import app_context
from includes.db.dataclass import _QuizQuestion
from includes.schemas.cache.dataclass import QuizQuesCache
from includes.db.models.secondary import QuizQuestion, QuizRelationships

QuizQuestionCacheData = QuizQuesCache()


class QuizQuestionCache:

    @staticmethod
    def _cache(record: QuizQuestion) -> _QuizQuestion:
        _record = record.to_dict()
        QuizQuestionCacheData.ById[record.id] = _record

        return _record

    @staticmethod
    async def get(id: int) -> _QuizQuestion:
        record = QuizQuestionCacheData.ById.get(id)
        if record:
            return record

        record = app_context.db.query(QuizQuestion).filter_by(id=id).first()
        if not record:
            return None
        return QuizQuestionCache._cache(record)

    @staticmethod
    async def get_many(id_list: list[int]):
        records = []
        missing = []

        for qid in id_list or []:
            record = QuizQuestionCacheData.ById.get(qid)
            records.append(record) if record else missing.append(qid)

        if missing:
            records.extend(
                QuizQuestionCache._cache(r)
                for r in app_context.db.query(QuizQuestion)
                .filter(QuizQuestion.id.in_(missing))
                .all()
            )

        return records

    @staticmethod
    async def get_first_by_terms_id(terms_id: int):
        if QuizQuestionCacheData.ByTermId.get(terms_id):
            return await QuizQuestionCache.get(QuizQuestionCacheData.ByTermId[terms_id])

        record = (
            app_context.db.query(QuizQuestion)
            .join(QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id)
            .filter(QuizRelationships.terms_id == terms_id)
            .first()
        )

        if not record:
            return None

        QuizQuestionCacheData.ByTermId[terms_id] = record.id
        return QuizQuestionCache._cache(record)
