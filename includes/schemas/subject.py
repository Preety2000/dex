import asyncio

from httpx2 import query
from sqlalchemy import asc

from includes.core.globals.entry import app_context, GlobleCatch
from includes.admin.api.schemas import subject
from includes.db.models.owner import Subject
from includes.db.dataclass import to_dict
from includes.schemas.cache.mcq_question import QuizQuestionCache
from includes.schemas.cache.terms import TermsCache
from includes.schemas.cache.subject import SubjectCache


class ClassSubject:

    @staticmethod
    def get(query=None, quet=None):
        subject =app_context.db.query(Subject)

        if query is True and isinstance(query, bool):
            all_subjects = subject.order_by(asc(Subject.name)).all()
            return [to_dict(item.to_dataclass()) for item in all_subjects]

        if isinstance(query, int) or (isinstance(query, str) and query.isdigit()):
            subject_query = subject.filter(Subject.id == int(query)).first()
        else:
            subject_query = subject.filter(
                (Subject.slug == query) | (Subject.name == query)
            ).first()

        return to_dict(subject_query.to_dataclass()) if quet is None else subject_query

    @staticmethod
    async def get_with_terms():

        if GlobleCatch.get_with_terms:
            return GlobleCatch.get_with_terms

        grouped = []

        subject_list = await SubjectCache.get_all()
        terms_list = await asyncio.gather(
            *(TermsCache.get_by_subject(subject.id) for subject in subject_list)
        )

        async def add_first_mcq(term):
            term.first_mcq = await QuizQuestionCache.get_first_by_terms_id(term.id)
            return to_dict(term)

        for subject, terms in zip(subject_list, terms_list):
            quu = to_dict(subject)
            quu.update({"terms": [await add_first_mcq(term) for term in terms]})
            grouped.append(quu)

        GlobleCatch.get_with_terms = grouped
        return grouped
