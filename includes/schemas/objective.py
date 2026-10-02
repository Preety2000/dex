# For MCQ Question
import inspect

from includes.core.globals.entry import app_context
from includes.core.globals.coreutils import format_view_count
from sqlalchemy import asc, desc, func, or_, select
from includes.core.pagination import Pagination
from includes.core.query_paginator import QueryPaginator
from includes.core.new_query_paginator import NewQueryPaginator
from includes.core.request_filter import RequestFilter
from includes.db.connection import active_secondary_db
from includes.db.dataclass import _QuizQuestion, serialize, to_dict
from includes.db.models.secondary import QuizQuestion, QuizRelationships, Terms


from typing import  Tuple, Optional, List
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.cache.terms import TermsCache
from includes.schemas.subject import ClassSubject


async def get_mcq_json(
    item: Optional[QuizQuestion] = None,
    *,
    subject=None,
    title=None,
    **more,
) -> Tuple[ object]:
    response = {}

    if not item:
        return response

    item.next_prev_question()

    record = item.to_dict(**more)
    response = to_dict(record)
    response.update(
        {
            "options": sorted(
                set(response["incorrect_answers"] + [response["correct_answer"]])
            ),
            "views_formatted": format_view_count(response["views"]),
            "sno": getattr(item, "sno", 1),
            "prev": await get_mini_mcq_json(item.prev),
            "next": await get_mini_mcq_json(item.next),
        }
    )

    if title:
        response["title"] = getattr(item, "question")
        del response["question"]

    del response["incorrect_answers"]

    if subject:
        response["subject"] = to_dict(await SubjectCache.get_by_id(item.subject_id))

    return response


async def get_mini_mcq_json(
    item: Optional[QuizQuestion] = None,
    *,
    subject=None,
    title=None,
    **more,
) -> Tuple[ object]:
    response = {}

    if not item:
        return response

    record = item.to_dict(**more)
    response = to_dict(record)

    response.update(
        {
            "options": sorted(
                set(response["incorrect_answers"] + [response["correct_answer"]])
            ),
            "views_formatted": format_view_count(response["views"]),
            "sno": getattr(item, "sno", 1),
        }
    )

    if title:
        response["title"] = getattr(item, "question")
        del response["question"]

    del response["incorrect_answers"]

    if subject:
        response["subject"] = to_dict(await SubjectCache.get_by_id(item.subject_id))

    return response


async def get_mcq_by_terms_id__(*, terms_id, limit=4, **more):

    practice = (
        app_context.db.query(QuizQuestion)
        .join(QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id)
        .filter(QuizRelationships.terms_id == terms_id)
    )

    practice = practice.filter(QuizQuestion.status == "Publish")

    if not more:
        return [item.to_dict() for item in practice.limit(limit).all()]

    data = await QueryPaginator.paginate(
        types="query",
        query=practice,
        model=QuizQuestion,
        transform=lambda item: item.to_dict(),
        limit=limit,
        **more,
    )
    return data.records


@staticmethod
async def get_mcq_by_terms_id(*, terms_id, limit=4, **more):
    if terms_id is None:
        return []

    # Safe term_id resolution (if passed as Model/Object instance)
    if hasattr(terms_id, "id"):
        terms_id = terms_id.id

    # Modern SQLAlchemy 2.0 select query construction
    query = (
        select(QuizQuestion)
        .join(QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id)
        .where(
            QuizRelationships.terms_id == terms_id,
            QuizQuestion.status == "Publish",
        )
        .distinct()
    )

    # Secondary DB Resolve
    db = await active_secondary_db()

    # Dynamic Column Filtering from **more kwargs
    remaining_kwargs = {}
    for key, value in list(more.items()):
        if value is not None and (column := getattr(QuizQuestion, key, None)):
            clean_value = getattr(value, "id", value) if hasattr(value, "id") else value
            if isinstance(clean_value, (int, str, float, bool)):
                query = query.where(column == clean_value)
            else:
                remaining_kwargs[key] = value
        else:
            remaining_kwargs[key] = value

    # Paginated Execution with NewQueryPaginator
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
        questions = app_context.db.query(QuizQuestion)

        if terms_id:
            questions = questions.join(
                QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id
            ).filter(QuizRelationships.terms_id == terms_id)

        for key, value in more.items():
            if hasattr(QuizQuestion, key) and value is not None:
                questions = questions.filter(getattr(QuizQuestion, key) == value)

        questions = questions.filter(QuizQuestion.status == "Publish")
        record = questions.first()
        return await get_mcq_json(record, subject=True) if record else None

    @staticmethod
    async def getmcq_list__(term_slug=None, *, limit=10, **more):

        if not term_slug or term_slug == "default":
            data = await QueryPaginator.paginate(
                types="query",
                query=app_context.db.query(QuizQuestion),
                model=QuizQuestion,
                transform=lambda item: get_mini_mcq_json(item),
                limit=limit,
                **more,
            )
            return data.records, {"name": "Default"}

        terms_query = await TermsCache.get_by_slug(term_slug)
        if terms_query:
            quizquestion = (
                app_context.db.query(QuizQuestion)
                .join(QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id)
                .filter(QuizRelationships.terms_id == terms_query.id)
            )

            quizquestion = quizquestion.filter(QuizQuestion.status == "Publish")
            data = await QueryPaginator.paginate(
                types="query",
                query=quizquestion,
                model=QuizQuestion,
                transform=lambda item: get_mini_mcq_json(item),
                limit=limit,
                **more,
            )
            return data.records, serialize(terms_query)

        return None, None

    @staticmethod
    async def getmcq_list(term_slug=None, *, limit=10, **more):
        db = await active_secondary_db()

        # Case 1: Default Query (No specific term_slug or "default")
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

        # Case 2: Query by term_slug
        terms_query = await TermsCache.get_by_slug(term_slug)
        if terms_query:
            term_id = getattr(terms_query, "id", terms_query)

            query = (
                select(QuizQuestion)
                .join(QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id)
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

        return None, None

    @staticmethod
    async def at_tests__(
        subject,
        category,
        limit=10,
        ids=None,
        *,
        co_search: str = None,
        **options: Optional[List[str]],
    ):
        quizquestion = app_context.db.query(QuizQuestion)

        if category != "default":
            terms_query = (
                app_context.db.query(Terms).filter(Terms.name == category).first()
            )
            if terms_query:
                quizquestion = (
                    app_context.db.query(QuizQuestion)
                    .join(
                        QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id
                    )
                    .filter(QuizRelationships.terms_id == terms_query.id)
                )

        if co_search is not None and co_search != "default":
            terms_query = (
                app_context.db.query(Terms).filter(Terms.slug == co_search).first()
            )
            if terms_query:
                quizquestion = (
                    app_context.db.query(QuizQuestion)
                    .join(
                        QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id
                    )
                    .filter(QuizRelationships.terms_id == terms_query.id)
                )

        if subject != "All Subject":
            db_subject = ClassSubject.get(subject)
            quizquestion = quizquestion.filter(
                QuizQuestion.subject_id == db_subject.get("id")
            )

        if isinstance(ids, list):
            quizquestion = quizquestion.filter(~QuizQuestion.id.in_(ids))

        quizquestion = quizquestion.filter(QuizQuestion.status == "Publish")
        quizquestion = quizquestion.order_by(
            func.random() if "random" in options else asc(QuizQuestion.id)
        )

        quizquestion = await RequestFilter.apply_request_filters(
            model=QuizQuestion,
            request_type="referer",
            query=quizquestion,
            columns={"question": "title"},
            search_columns=["title", "excerpt"],
        )

        if "results" in options:
            total = quizquestion.count()
            pagination = Pagination("referer")
            await pagination.load()
            offset = pagination.get_offset(limit=limit)

            records = quizquestion.offset(offset).limit(pagination.limit).all()

            async def enrich_student(record):
                return await get_mini_mcq_json(record, subject=True, title=True)

            processed_data, pagination_data, total = await pagination.paginate(
                total=total,
                data=records,
                transform=enrich_student,
            )

            getList = [
                "id",
                "title",
                "correct_answer",
                "options",
                "subject",
                "category",
                "sno",
            ]
            data_querys = [{it: xv.get(it) for it in getList} for xv in processed_data]
            return data_querys, pagination_data, total

        quizquestion = quizquestion.limit(int(limit)).all()
        return [await get_mini_mcq_json(item) for item in quizquestion]

    @staticmethod
    async def at_tests(
        subject,
        category,
        limit=10,
        ids=None,
        *,
        co_search: str = None,
        **options,
    ):
        db = await active_secondary_db()

        # Base SQLAlchemy 2.0 Async Select Statement
        query = select(QuizQuestion)

        # Filter by Category
        if category != "default":
            terms_stmt = select(Terms).where(Terms.name == category)
            res_terms = db.execute(terms_stmt)
            if inspect.isawaitable(res_terms):
                res_terms = await res_terms
            terms_query = res_terms.scalars().first()

            if terms_query:
                query = query.join(
                    QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id
                ).where(QuizRelationships.terms_id == terms_query.id)

        # Filter by co_search slug
        if co_search is not None and co_search != "default":
            terms_stmt = select(Terms).where(Terms.slug == co_search)
            res_terms = db.execute(terms_stmt)
            if inspect.isawaitable(res_terms):
                res_terms = await res_terms
            terms_query = res_terms.scalars().first()

            if terms_query:
                query = query.join(
                    QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id
                ).where(QuizRelationships.terms_id == terms_query.id)

        # Filter by Subject
        if subject != "All Subject":
            db_subject = ClassSubject.get(subject)
            if db_subject and db_subject.get("id"):
                query = query.where(QuizQuestion.subject_id == db_subject.get("id"))

        # Exclude IDs if passed
        if isinstance(ids, list) and ids:
            query = query.where(~QuizQuestion.id.in_(ids))

        # Status and Distinct
        query = query.where(QuizQuestion.status == "Publish").distinct()

        # Ordering Logic
        if "random" in options or options.get("random"):
            query = query.order_by(func.random())
        else:
            query = query.order_by(asc(QuizQuestion.id))

        # Apply Request Filters if configured
        query = await RequestFilter.apply_request_filters(
            model=QuizQuestion,
            request_type="referer",
            query=query,
            columns={"question": "title"},
            search_columns=["title", "excerpt"],
        )

        # Case 1: Paginated Execution (when "results" flag is present)
        if "results" in options or options.get("results"):

            async def enrich_student(record):
                mcq_json = await get_mini_mcq_json(record, subject=True, title=True)
                get_list = [
                    "id",
                    "title",
                    "correct_answer",
                    "options",
                    "subject",
                    "category",
                    "sno",
                ]
                return {it: mcq_json.get(it) for it in get_list}

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

            return data.records, data.pagination, data.total_count

        # Case 2: Simple List Execution (without full pagination envelope)
        stmt = query.limit(int(limit))
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res

        records = res.scalars().all()

        return [
            (
                await get_mini_mcq_json(item)
                if inspect.iscoroutinefunction(get_mini_mcq_json)
                else get_mini_mcq_json(item)
            )
            for item in records
        ]
