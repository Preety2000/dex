from datetime import datetime, time
import random
import re
import asyncio

from sqlalchemy import select, or_, desc, func

from includes.database.connection import active_primary_db, active_secondary_db
from includes.utils._sub import distribute_amount
from includes.api.exam.results.results_practice import SELF_RESULTS
from includes.core.config import exam_database
from includes.core.globals.entry import app_context
from includes.database.models.db_exam import (
    _ExamRecord,
    PracticeExamRecord,
)
from includes.function import get_unique_id
from includes.database.models.owner import Subject
from includes.database.models.secondary import (
    QuizQuestion,
    QuizRelationships,
    Terms,
)
from includes.api.exam.student import RecordType, Student
from includes.api.exam.session.es import ES
from includes.utils.exm import (
    error_exam_message,
    exam_submitted_message,
)
from includes.api.exam.metadata import limitStatusHtml
from includes.schemas.cache.terms import TermsCache
from includes.schemas.cache.subject import SubjectCache
from includes.utils.utils import (
    get_post_value,
    get_query_value,
    get_referer_value,
    json_response,
)

# Start and end of today in milliseconds
start_of_day = int(
    datetime.combine(
        datetime.today(),
        time.min,
    ).timestamp()
)

end_of_day = int(
    datetime.combine(
        datetime.today(),
        time.max,
    ).timestamp()
)


async def build_subject_category():
    subjects = ["All Subject"]
    seen_subjects = set()

    category = [
        {
            "subject": "Any",
            "count": 1000,
            "entry": ["default", "All Category"],
        }
    ]

    # Step 1: fetch all subjects
    subject_list = await SubjectCache.get_all()

    # Step 2: parallel fetch of terms
    terms_list = await asyncio.gather(
        *(TermsCache.get_by_subject(subject.id) for subject in subject_list)
    )

    # Step 3: process results
    for subject, terms in zip(
        subject_list,
        terms_list,
    ):
        for term in terms:
            if term.mcq_count and term.mcq_count > 5:
                seen_subjects.add(subject.name)

                category.append(
                    {
                        "subject": subject.name,
                        "count": term.mcq_count,
                        "entry": [
                            term.slug,
                            term.name,
                        ],
                    }
                )

    subjects.extend(sorted(seen_subjects))

    return subjects, category


async def get_exam_json(record: _ExamRecord):
    result_data = await SELF_RESULTS.get_exam_result(record)

    result = {
        "result_no": result_data[0][0],
        "exam_name": result_data[0][1],
        "category": result_data[0][2],
        "published": result_data[0][3],
        "result_year": result_data[0][4],
        "total_questions": result_data[1][0],
        "incorrect_count": result_data[1][1],
        "correct_count": result_data[1][2],
        "skipped_count": result_data[1][3],
        "attempt_questions": result_data[1][4],
        "paper": result_data[2][0],
        "total_marks": result_data[3][0],
        "total_obtained_marks": result_data[3][1],
        "percentage": result_data[3][2],
        "marks_in_word": result_data[3][3],
        "total_grade": result_data[3][4],
        "result": result_data[3][5],
        "sname": result_data[4][0],
        "roll_number": result_data[4][1],
        "registration_number": result_data[4][2],
        "image": result_data[4][3],
        "examinant": result_data[5][0],
        "instructor": result_data[5][1],
    }

    return result


class SELF_EXAM_MANAGER:

    def __init__(self):
        self.request = app_context.request
        self.function = app_context.function

    async def insert_self_exam_row_data(
        self,
        roll_no,
        submit,
        ismeta,
    ):
        with exam_database() as db:
            new_record = PracticeExamRecord(
                roll_no=roll_no,
                content=submit,
                ismeta=ismeta,
            )

            db.add(new_record)
            db.commit()

            return new_record.keys

    async def get_exam_key(
        self,
        roll_no,
        exam_questions,
        ismeta,
    ):
        query = {}

        for subject, questions in exam_questions.items():
            query.setdefault(subject, [])

            for q in questions:
                options = q["options"][:]
                random.shuffle(options)

                query[subject].append(
                    [
                        q["id"],
                        options,
                        None,
                    ]
                )

        return await self.insert_self_exam_row_data(
            roll_no,
            query,
            ismeta,
        )

    async def get_exam_question_by_subject(self, subject, category, question_limit):
        subject_name = "Default"
        category_name = "Default"

        # Base SELECT
        quiz_stmt = select(QuizQuestion)

        # Category filter
        db = await active_secondary_db()
        if category != "default":

            terms_stmt = select(Terms).where(Terms.slug == category)
            terms_query = db.execute(terms_stmt).scalar_one_or_none()

            if terms_query:
                category_name = terms_query.name

                quiz_stmt = quiz_stmt.join(
                    QuizRelationships,
                    QuizRelationships.quiz_id == QuizQuestion.id,
                ).where(QuizRelationships.terms_id == terms_query.id)

        # Subject filter
        if subject:

            if isinstance(subject, int) or (
                isinstance(subject, str) and subject.isdigit()
            ):
                subject_stmt = select(Subject).where(Subject.id == int(subject))
            else:
                subject_stmt = select(Subject).where(Subject.name == subject)

            db2 = await active_primary_db()
            db_subject = db2.execute(subject_stmt).scalar_one_or_none()

            if db_subject:
                subject_name = db_subject.name

                quiz_stmt = quiz_stmt.where(QuizQuestion.subject_id == db_subject.id)

        # Get questions
        quiz_stmt = quiz_stmt.order_by(
            func.random(),
            desc(QuizQuestion.id),
        ).limit(int(question_limit))

        quizquestion = db.execute(quiz_stmt).scalars().all()

        def get_option(query):
            incorrect_answers = query.incorrect_answers

            return sorted(incorrect_answers + [query.correct_answer])

        data_querys = []
        submit = []

        for i, query in enumerate(quizquestion):

            # Get categories for question
            categories_stmt = (
                select(Terms)
                .join(
                    QuizRelationships,
                    QuizRelationships.terms_id == Terms.id,
                )
                .where(QuizRelationships.quiz_id == query.id)
            )

            allCategories = db.execute(categories_stmt).scalars().all()

            data_querys.append(
                {
                    "id": query.id,
                    "title": query.question,
                    "category": [cat.name for cat in allCategories],
                    "sno": i,
                }
            )

            option = get_option(query)
            random.shuffle(option)

            submit.append(
                [
                    query.id,
                    option,
                    None,
                ]
            )

        return (
            subject_name,
            category_name,
            data_querys,
            submit,
        )

    async def index(self, response):
        post = get_post_value

        roll_no = await app_context.setting.member("roll_no")

        language = await app_context.setting.get("language")

        daily_limit, monthly_limit = await Student.has_submission_limit_exceeded(
            roll_no
        )

        if daily_limit is True and language:
            response["__ac"] = 102
            response["title"] = limitStatusHtml[language]["title"]
            response["content"] = limitStatusHtml[language]["content"]

        else:
            timing = await post("timing")
            subject = await post("subject")
            category = await post("category")
            nim_que = await post("Nq")

            if subject and category and nim_que:

                mcqlist_count_list = await SubjectCache.get_mcqlist_count(
                    category,
                    (
                        None
                        if re.sub(
                            r"\s+",
                            "",
                            subject,
                        ).lower()
                        == "allsubject"
                        else subject
                    ),
                )

                details = {}
                content = {}
                question = {}

                for sub_id, q_length in distribute_amount(
                    mcqlist_count_list,
                    int(nim_que),
                    True,
                ).items():

                    pepar = f"pe{sub_id}"

                    sub_name, cotg_name, ques, content[pepar] = (
                        await self.get_exam_question_by_subject(
                            sub_id, category, q_length
                        )
                    )

                    question[pepar] = ques

                    details[pepar] = [
                        len(ques),
                        sub_name,
                        cotg_name,
                        len(ques),
                        1,
                        None,
                    ]

                if category != "default":

                    category_ = await TermsCache.get_by_slug(category)

                    if category_:
                        category = category_.name

                keys = await Student.self_insert(
                    roll_no,
                    content,
                    {
                        "details": details,
                        "questions": question,
                        "info": [
                            int(timing),
                            subject,
                            category,
                            nim_que,
                        ],
                    },
                )

                response["jump"] = f"/exam?hx={keys}"

            else:
                (
                    response["subjects"],
                    response["category"],
                ) = await build_subject_category()

                if get_referer_value("isme"):
                    response["__ac"] = 101
                else:
                    response["__ac"] = 100

        return json_response(response)

    async def get(self, keys):
        roll_no = await app_context.setting.member("roll_no")

        exam = await Student.get_by_exam_key(
            keys,
            RecordType.STUDENT,
        )

        if not exam or exam.roll_no != roll_no:
            return None

        if exam.is_submitted:
            return True

        session_key = get_unique_id()

        ES.add(
            roll_no,
            session_key,
        )

        return {"session_key": session_key}

    async def session_inject(
        self,
        response,
        hxs_keys,
    ):
        lists = await self.get(hxs_keys)

        if lists is True:
            response["__ac"] = 116

            href = f"/exam/result/do/{hxs_keys}"

            response["content"] = exam_submitted_message(href)

            return response

        if lists:
            response.update(lists)
            response["__ac"] = 107
            return response

        response["content"] = error_exam_message()
        response["__ac"] = 116

        return response
