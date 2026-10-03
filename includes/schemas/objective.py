import inspect
from typing import Tuple, Optional, List

from sqlalchemy import asc, func, select

from includes.core.globals.entry import app_context
from includes.core.globals.coreutils import format_view_count
from includes.core.paginator import NewQueryPaginator
from includes.core.request_filter import RequestFilter
from includes.db.connection import active_secondary_db
from includes.db.dataclass import serialize, to_dict
from includes.db.models.secondary import (
    QuizQuestion,
    QuizRelationships,
    Terms,
)
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.cache.terms import TermsCache
from includes.schemas.subject import ClassSubject


async def get_mcq_json(
    item: Optional[QuizQuestion] = None,
    *,
    subject=None,
    title=None,
    **more,
) -> dict:

    if not item:
        return {}

    item.next_prev_question()

    response = to_dict(item.to_dict(**more))

    response.update(
        {
            "options": sorted(
                set(
                    response.get("incorrect_answers", [])
                    + [response.get("correct_answer")]
                )
            ),
            "views_formatted": format_view_count(response.get("views", 0)),
            "sno": getattr(item, "sno", 1),
            "prev": await get_mini_mcq_json(item.prev),
            "next": await get_mini_mcq_json(item.next),
        }
    )

    if title:
        response["title"] = getattr(item, "question", "")
        response.pop("question", None)

    response.pop("incorrect_answers", None)

    if subject:
        response["subject"] = to_dict(await SubjectCache.get_by_id(item.subject_id))

    return response


async def get_mini_mcq_json(
    item: Optional[QuizQuestion] = None,
    *,
    subject=None,
    title=None,
    **more,
) -> dict:

    if not item:
        return {}

    response = to_dict(item.to_dict(**more))

    response.update(
        {
            "options": sorted(
                set(
                    response.get("incorrect_answers", [])
                    + [response.get("correct_answer")]
                )
            ),
            "views_formatted": format_view_count(response.get("views", 0)),
            "sno": getattr(item, "sno", 1),
        }
    )

    if title:
        response["title"] = getattr(item, "question", "")
        response.pop("question", None)

    response.pop("incorrect_answers", None)

    if subject:
        response["subject"] = to_dict(await SubjectCache.get_by_id(item.subject_id))

    return response


async def get_mcq_by_terms_id(
    *,
    terms_id,
    limit=4,
    **more,
):
    if terms_id is None:
        return []

    if hasattr(terms_id, "id"):
        terms_id = terms_id.id

    db = await active_secondary_db()

    query = (
        select(QuizQuestion)
        .join(
            QuizRelationships,
            QuizRelationships.quiz_id == QuizQuestion.id,
        )
        .where(
            QuizRelationships.terms_id == terms_id,
            QuizQuestion.status == "Publish",
        )
        .distinct()
    )

    remaining_kwargs = {}

    for key, value in more.items():
        column = getattr(QuizQuestion, key, None)

        if column is not None and value is not None:
            value = getattr(value, "id", value)

            if isinstance(value, (int, str, float, bool)):
                query = query.where(column == value)
            else:
                remaining_kwargs[key] = value
        else:
            remaining_kwargs[key] = value

    data = await NewQueryPaginator.paginate(
        types="query",
        query=query,
        model=QuizQuestion,
        limit=limit,
        db=db,
        transform=lambda item: item.to_dict(),
        **remaining_kwargs,
    )

    return data.records


class ClassObjective:

    @staticmethod
    async def get(*, terms_id=None, **more):

        db = await active_secondary_db()

        query = select(QuizQuestion)

        if terms_id:
            query = query.join(
                QuizRelationships,
                QuizRelationships.quiz_id == QuizQuestion.id,
            ).where(QuizRelationships.terms_id == terms_id)

        query = query.where(QuizQuestion.status == "Publish")

        for key, value in more.items():
            column = getattr(QuizQuestion, key, None)

            if column is not None and value is not None:
                query = query.where(column == value)

        query = query.limit(1)

        result = db.execute(query)

        if inspect.isawaitable(result):
            result = await result

        record = result.scalars().first()

        if not record:
            return None

        return await get_mcq_json(
            record,
            subject=True,
        )

    @staticmethod
    async def getmcq_list(
        term_slug=None,
        *,
        limit=10,
        **more,
    ):

        db = await active_secondary_db()

        # Default questions
        if not term_slug or term_slug == "default":

            query = select(QuizQuestion).where(QuizQuestion.status == "Publish")

            data = await NewQueryPaginator.paginate(
                types="query",
                query=query,
                model=QuizQuestion,
                limit=limit,
                db=db,
                transform=lambda item: get_mini_mcq_json(item),
                **more,
            )

            return data.records, {"name": "Default"}

        # Resolve term
        terms_query = await TermsCache.get_by_slug(term_slug)

        if not terms_query:
            return None, None

        term_id = getattr(
            terms_query,
            "id",
            terms_query,
        )

        query = (
            select(QuizQuestion)
            .join(
                QuizRelationships,
                QuizRelationships.quiz_id == QuizQuestion.id,
            )
            .where(
                QuizRelationships.terms_id == term_id,
                QuizQuestion.status == "Publish",
            )
            .distinct()
        )

        data = await NewQueryPaginator.paginate(
            types="query",
            query=query,
            model=QuizQuestion,
            limit=limit,
            db=db,
            transform=lambda item: get_mini_mcq_json(item),
            **more,
        )

        return data.records, serialize(terms_query)

    @staticmethod
    async def at_tests(
        subject,
        category,
        limit=10,
        ids=None,
        *,
        co_search=None,
        **options,
    ):

        db = await active_secondary_db()

        query = select(QuizQuestion)

        # ----------------------------------
        # Category
        # ----------------------------------

        if category != "default":

            terms_stmt = select(Terms.id).where(Terms.name == category)

            result = db.execute(terms_stmt)

            if inspect.isawaitable(result):
                result = await result

            terms_id = result.scalar()

            if terms_id:
                query = query.join(
                    QuizRelationships,
                    QuizRelationships.quiz_id == QuizQuestion.id,
                ).where(QuizRelationships.terms_id == terms_id)

        # ----------------------------------
        # Co-search
        # ----------------------------------

        if co_search and co_search != "default":

            terms_stmt = select(Terms.id).where(Terms.slug == co_search)

            result = db.execute(terms_stmt)

            if inspect.isawaitable(result):
                result = await result

            terms_id = result.scalar()

            if terms_id:
                query = query.join(
                    QuizRelationships,
                    QuizRelationships.quiz_id == QuizQuestion.id,
                ).where(QuizRelationships.terms_id == terms_id)

        # ----------------------------------
        # Subject
        # ----------------------------------

        if subject != "All Subject":

            db_subject = ClassSubject.get(subject)

            if db_subject and db_subject.get("id"):
                query = query.where(QuizQuestion.subject_id == db_subject["id"])

        # ----------------------------------
        # Exclude IDs
        # ----------------------------------

        if isinstance(ids, list) and ids:
            query = query.where(~QuizQuestion.id.in_(ids))

        # ----------------------------------
        # Status
        # ----------------------------------

        query = query.where(QuizQuestion.status == "Publish").distinct()

        # ----------------------------------
        # Ordering
        # ----------------------------------

        if options.get("random"):
            query = query.order_by(func.random())
        else:
            query = query.order_by(asc(QuizQuestion.id))

        # ----------------------------------
        # Request Filters
        # ----------------------------------

        query = await RequestFilter.apply_request_filters(
            model=QuizQuestion,
            request_type="referer",
            query=query,
            columns={"question": "title"},
            search_columns=[
                "title",
                "excerpt",
            ],
        )

        # ----------------------------------
        # Paginated result
        # ----------------------------------

        if options.get("results"):

            async def enrich_student(record):

                mcq_json = await get_mini_mcq_json(
                    record,
                    subject=True,
                    title=True,
                )

                fields = [
                    "id",
                    "title",
                    "correct_answer",
                    "options",
                    "subject",
                    "category",
                    "sno",
                ]

                return {key: mcq_json.get(key) for key in fields}

            data = await NewQueryPaginator.paginate(
                types="referer",
                query=query,
                model=QuizQuestion,
                limit=limit,
                db=db,
                transform=enrich_student,
                request_type="referer",
                **options,
            )

            return (
                data.records,
                data.pagination,
                data.total_count,
            )

        # ----------------------------------
        # Simple result
        # ----------------------------------

        query = query.limit(int(limit))

        result = db.execute(query)

        if inspect.isawaitable(result):
            result = await result

        records = result.scalars().all()

        return [await get_mini_mcq_json(record) for record in records]
