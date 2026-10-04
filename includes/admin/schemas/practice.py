from sqlalchemy import case, delete, func, or_, select

from includes.admin.api.schemas.practice import AdminApiMCQ
from includes.admin.modals import checked, emptyMessage
from includes.admin.schemas.backup import ClassBeckup
from includes.core.globals.coreutils import is_empty
from includes.core.globals.entry import app_context
from includes.core.metadata import MetaData
from includes.core.paginator import NewQueryPaginator
from includes.database.connection import active_secondary_db
from includes.database.dataclass.dataclass import serialize
from includes.database.models.secondary import QuizQuestion, QuizRelationships
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.cache.terms import TermsCache
from includes.schemas.router_schema import DynamicURLRoute
from includes.utils.utils import get_post_value, get_query_value, set_response


class ClassObjective:

    # ==========================================
    # SELECT / FETCH METHODS
    # ==========================================

    @staticmethod
    async def get_list(limit=None):
        db = await active_secondary_db()

        stmt = select(
            func.count(QuizQuestion.id).label("total"),
            func.count(case((QuizQuestion.status == "Draft", 1))).label("draft"),
            func.count(case((QuizQuestion.status == "Publish", 1))).label("publish"),
        )

        result = db.execute(stmt).one()

        set_response("total", result.total)
        set_response("draft", result.draft)
        set_response("publish", result.publish)

        data = await NewQueryPaginator.paginate(
            db=db,
            limit=limit,
            types="query",
            model=QuizQuestion,
            query=select(QuizQuestion),
            transform=lambda item: item.to_dict(),
        )

        return data.records

    @staticmethod
    async def get_by_id(item_id: int):
        """Find a single QuizQuestion by ID."""

        if not item_id:
            return None

        db = await active_secondary_db()

        stmt = select(QuizQuestion).where(QuizQuestion.id == int(item_id))

        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    async def get_by_question(question_text: str):
        """Find a single QuizQuestion by Question text."""

        if not question_text:
            return None

        db = await active_secondary_db()

        stmt = select(QuizQuestion).where(QuizQuestion.question == question_text)

        return db.execute(stmt).scalar_one_or_none()

    # ==========================================
    # CATEGORY RELATIONSHIP
    # ==========================================

    @staticmethod
    async def add_category(db, quiz_id, data_querys):
        categories = data_querys.get(
            "category",
            [],
        )

        categories = list(map(int, categories)) if categories else []

        # Delete existing relationships
        stmt = delete(QuizRelationships).where(QuizRelationships.quiz_id == quiz_id)

        db.execute(stmt)
        db.flush()

        # Add updated categories
        if categories:
            db.add_all(
                [
                    QuizRelationships(
                        terms_id=terms_id,
                        quiz_id=quiz_id,
                    )
                    for terms_id in categories
                ]
            )

    # ==========================================
    # INSERT / CREATE METHODS
    # ==========================================

    @staticmethod
    async def insert(data_querys):

        def returnsError(query, errorType):
            app_context.response["error"] = (
                f"This post already exists with the "
                f"{errorType}: "
                f"{query.get(errorType.lower())}. "
                f"Please change the Question and save. "
                f"You can view the Question "
                f"<a target='_blank' "
                f"href='{query.get('url', '#')}'>"
                f"here</a>."
            )

            return data_querys

        # Validate through AdminApiMCQ schema check
        data = await AdminApiMCQ.insert()

        error = data.get("error") if isinstance(data, dict) else None

        if error is not None:
            app_context.response["error"] = error
            return data_querys

        if app_context.response.get("error"):
            return data_querys

        question = data_querys.get("question")

        # Duplicate Question check
        existing_question = await ClassObjective.get_by_question(question)

        if existing_question:
            return returnsError(
                existing_question.to_dict(),
                "Question",
            )

        # Create Record
        question_query = QuizQuestion(
            question=question,
            excerpt=data_querys.get("excerpt"),
            correct_answer=data_querys.get("correct_answer"),
            incorrect_answers=data_querys.get("incorrect_answers"),
            subject_id=int(data_querys.get("subject_id", 0)),
            status=data_querys.get("status"),
        )

        db = await active_secondary_db()

        db.add(question_query)
        db.flush()

        # Attach categories
        await ClassObjective.add_category(
            db,
            question_query.id,
            data_querys,
        )

        db.commit()

        if app_context.function.is_api():
            return [
                {
                    "insert": True,
                    "querys": question_query.to_dict(),
                }
            ]

        data_querys.update({"redirect": True})

        return data_querys

    async def insert_by_api(self, data):
        news = []
        existing = []

        for item_key, value in data.items():
            question_text = value.get("question")

            query = await ClassObjective.get_by_question(question_text)

            if query:
                existing.append(
                    [
                        value,
                        query.to_dict(),
                    ]
                )

            else:
                payload = {
                    "status": value.get("status"),
                    "question": question_text,
                    "excerpt": value.get("excerpt"),
                    "subject_id": value.get(
                        "subject",
                        0,
                    ),
                    "category": value.get(
                        "category",
                        [],
                    ),
                    "correct_answer": value.get("correct_answer"),
                    "incorrect_answers": value.get("incorrect_answers"),
                }

                ins = await ClassObjective.insert(payload)

                news.append(
                    [
                        value,
                        ins,
                    ]
                )

        return {
            "add": news,
            "exit": existing,
        }

    # ==========================================
    # UPDATE METHOD
    # ==========================================

    @staticmethod
    async def update(data_querys):
        if app_context.response.get("error"):
            return data_querys

        item_id = app_context.function.getRequestInt("item")

        question_query = await ClassObjective.get_by_id(item_id)

        if not question_query:
            app_context.response["error"] = "No question found to update."

            return data_querys

        question = data_querys.get(
            "question",
            question_query.question,
        )

        db = await active_secondary_db()

        # Check duplicate excluding current ID
        stmt = select(QuizQuestion).where(
            QuizQuestion.question == question,
            QuizQuestion.id != item_id,
        )

        extQuery = db.execute(stmt).scalar_one_or_none()

        if extQuery:
            app_context.response["error"] = (
                f"This post already exists with the "
                f"question: <b>{question}</b>. "
                f"Please change the Question and save. "
                f"You can view the Question "
                f"<a href='/admin/practice/update?"
                f"item={extQuery.id}'>here</a>."
            )

            return data_querys

        # Apply updates
        question_query.question = question

        question_query.correct_answer = data_querys.get(
            "correct_answer",
            question_query.correct_answer,
        )

        question_query.incorrect_answers = data_querys.get(
            "incorrect_answers",
            question_query.incorrect_answers,
        )

        question_query.excerpt = data_querys.get(
            "excerpt",
            question_query.excerpt,
        )

        question_query.subject_id = data_querys.get(
            "subject_id",
            question_query.subject_id,
        )

        question_query.status = data_querys.get(
            "status",
            question_query.status,
        )

        await ClassObjective.add_category(
            db,
            question_query.id,
            data_querys,
        )

        db.commit()

        app_context.response["message"] = (
            "Updated Question successfully. " "<a href='/admin/practice'>Back</a>"
        )

        return data_querys

    # ==========================================
    # DELETE & STATUS ACTIONS
    # ==========================================

    @staticmethod
    async def action(item_id, action_type):
        question_record = await ClassObjective.get_by_id(item_id)

        if not question_record:
            app_context.response["pop_message"] = (
                "Question not found. Error code: Ae8340"
            )

            return False

        db = await active_secondary_db()

        # Status Toggle
        if action_type in [
            "trash",
            "publish",
        ]:
            question_record.status = "Draft" if action_type == "trash" else "Publish"

            db.commit()

            return True

        # Permanent Delete
        if action_type == "delete":

            # Backup before deleting
            backup_status = await ClassBeckup.insert(
                question_record.to_dict(),
                "QuizQuestion",
            )

            if backup_status:

                question_id = question_record.id

                db.execute(delete(QuizQuestion).where(QuizQuestion.id == question_id))

                db.execute(
                    delete(QuizRelationships).where(
                        QuizRelationships.quiz_id == question_id
                    )
                )

                db.commit()

                return True

            app_context.response["pop_message"] = (
                "This 'Question' could not be deleted "
                "during backup. Error code: Ae8349"
            )

            return False

        app_context.response["pop_message"] = (
            "Invalid action requested. " "Error code: Ae8340"
        )

        return False

    # ==========================================
    # DATA COLLECTION / CONTROLLER ROUTER
    # ==========================================

    @staticmethod
    async def addCollection(querys):
        subject_id = querys.get("subject_id")
        queryCategories = querys.get(
            "category",
            [],
        )

        app_context.response["subjects"] = []

        for subject in await SubjectCache.get_all():
            item = serialize(subject)

            if checked(
                subject.id == int(subject_id or 0),
                item,
            ):
                querys["subject_name"] = subject.name

            app_context.response["subjects"].append(item)

        app_context.response["resources"] = []
        app_context.response["category"] = []

        category_ids = [
            int(i) if isinstance(i, (int, str)) else i.get("id")
            for i in queryCategories
        ]

        for category in await TermsCache.get_all():

            dictionary = {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "subject_id": category.subject_id,
            }

            if category.topic == 1:
                category_dictionary = dictionary.copy()

                checked(
                    category.id in category_ids,
                    category_dictionary,
                )

                app_context.response["category"].append(category_dictionary)

        return querys

    @staticmethod
    async def index(roots: DynamicURLRoute):
        isPostMethod = app_context.function.is_post()

        item_id = app_context.function.getRequestInt("item")

        action_type = get_query_value("action")

        # Handle Action
        if (
            item_id
            and action_type
            and await ClassObjective.action(
                item_id,
                action_type,
            )
        ):
            MetaData.redirect_url = "/admin/practice"

            return "redirect"

        # Handle Form Submissions
        if roots.scope_slug in (
            "insert",
            "update",
        ):
            data_querys = None

            if item_id:
                record = await ClassObjective.get_by_id(item_id)

                if record:
                    data_querys = record.to_dict()

            request_keynme = [
                "question",
                "excerpt",
                "correct_answer",
                "incorrect_answers[]",
                "subject_id",
                "status",
                "category[]",
            ]

            default_values = [
                "",
                " ",
                "",
                "",
                "",
                "",
                [],
            ]

            if isPostMethod:
                data_querys = await get_post_value(
                    request_keynme,
                    default_values,
                )

                for key_name, value in data_querys.items():

                    if is_empty(value) and key_name not in ["excerpt"]:
                        app_context.response["error"] = app_context.response.get(
                            "error"
                        ) or emptyMessage(
                            key_name,
                            roots.scope_slug,
                        )

            if not data_querys and not isPostMethod:
                data_querys = {
                    key.replace("[]", ""): default_values[i]
                    for i, key in enumerate(request_keynme)
                }

                data_querys.update(
                    {
                        "incorrect_answers": [
                            "",
                            "",
                            "",
                        ]
                    }
                )

            bind_function = getattr(
                ClassObjective,
                roots.scope_slug,
                None,
            )

            if isPostMethod and callable(bind_function):
                bind_value = await bind_function(data_querys)

                if bind_value and bind_value.get("redirect"):
                    MetaData.redirect_url = "/admin/practice"

                    return "redirect"

            app_context.response["data_querys"] = await ClassObjective.addCollection(
                data_querys
            )

            return "admin/add_mcq"

        # Default GET list
        app_context.response["data_querys"] = await ClassObjective.get_list(10)

        return "admin/practice"
