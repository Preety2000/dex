import base64
import random
from dataclasses import dataclass, fields

from includes.api.exam.session.ch import ExamCacheMemory, ExamContext
from includes.api.exam.manager.practice import build_subject_category
from includes.core.globals.entry import app_context
from includes.api.exam.metadata import exam_category
from includes.core.security import _Security
from includes.db.models.db_exam import ExamDetails, TeacherProfile
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.cache.terms import TermsCache
from includes.schemas.objective import ClassObjective
from includes.schemas.subject import ClassSubject
from includes.utils.utils import get_post_value, get_referer_value, json_response


@dataclass(slots=True)
class CreateExam:

    inte: str | None = None
    questions: list | None = None
    examPreferences: list | None = None

    subject: str | None = None
    category: str | None = None
    oictionary: list | None = None
    question_submit: str | None = None

    async def load(self):

        for item in CREATE_FIELDS:
            setattr(self, item, await get_post_value(item))


CREATE_FIELDS = tuple(x.name for x in fields(CreateExam))


class ExamCreatePage:

    @staticmethod
    async def getCategoryBySubject(query):

        count, subject = query

        category = [
            {"subject": subject, "count": 1000, "entry": ["default", "All Category"]}
        ]

        subjects_data = await ClassSubject.get_with_terms()

        if not subject:

            result = ["All Subject"]

            for item in subjects_data:

                terms = item.get("terms") or []

                if max((x.get("mcq_count", 0) for x in terms), default=0) >= 10:
                    result.append(item.get("name"))

            return result

        for item in subjects_data:

            subject_name = item.get("name")

            if subject != "All Subject" and subject_name != subject:
                continue

            for term in item.get("terms") or []:

                mcq_count = term.get("mcq_count", 0)

                if mcq_count >= count:

                    category.append(
                        {
                            "subject": subject_name,
                            "count": mcq_count,
                            "entry": [term.get("slug"), term.get("name")],
                        }
                    )

        return category

    @staticmethod
    def extract_missing_key_and_ids(data, exam_meta):

        missing = None
        selected = []
        summary = []

        for key, value in data.items():

            if value is None:

                if missing is None:
                    missing = key

            elif isinstance(value, list):

                selected.extend(x["id"] for x in value)

            meta = exam_meta[key]

            summary.append([key, value is not None, f"{meta[1]} ~ {meta[2]}"])

        return missing, selected, summary

    @staticmethod
    async def insurt_exam_preferences_on_database(exam_name, details, questions):

        def generate_id(db):

            while True:

                uid = random.randint(100000000, 999999999)

                if not db.query(ExamDetails.id).filter(ExamDetails.id == uid).first():

                    return uid

        db = await app_context.db.configure_exam()
        member = await app_context.setting.member()
        exam_id = generate_id(db)

        teacher = (
            db.query(TeacherProfile)
            .filter(TeacherProfile.id == member.get("id"))
            .first()
        )

        db.add(
            ExamDetails(
                id=exam_id,
                teacher_id=teacher.id,
                join_mode=teacher.join_mode,
                open_request=teacher.open_request,
                req_appr_mode=teacher.req_appr_mode,
                result_visibility=teacher.result_visibility,
                exam_name=exam_name,
                details=details,
                questions=questions,
            )
        )

        db.commit()
        db.close()

        encoded = _Security.short_encode(str(exam_id))

        return app_context.request.referer.base_url.replace(
            "create",
            f"index?id={encoded}&_request_type=c7b4e436-ab36-4a93-834-565159552bdc&Jump=True",
        )

    @staticmethod
    async def insurt_exam_question(exam_context, entry):

        if exam_context is None:
            return {
                "__ac": 116,
                "index": True,
                "route": "expired_entry",
                "expired_entry": entry,
                "content": {
                    "title": "Session has expired",
                    "desc": [
                        f"Sorry, your session has expired. Please refresh and try again."
                    ],
                },
            }

        key, selected, paper = ExamCreatePage.extract_missing_key_and_ids(
            exam_context.exam_qsto, exam_context.exam_meta
        )

        if key:

            data = exam_context.exam_meta[key]
            limit, subject, category, *_ = data

            search_subject = get_referer_value("Cg")
            query, paginator, result = await ClassObjective.at_tests(
                subject, category, 20, selected, results=True, co_search=search_subject
            )

            co_list = []
            if "All Category" == category:
                _subject = await SubjectCache.get_by_name(subject)

                if _subject is None:
                    co_list = await TermsCache.get_all()
                else:
                    co_list = await TermsCache.get_by_subject(_subject.id)

                co_list = [
                    [f"{i.name} ({i.mcq_count})", i.slug]
                    for i in co_list
                    if i.mcq_count > 0
                ]

            return {
                "__ac": 112,
                "lists": query,
                "co_list": co_list,
                "results": result,
                "exam_name": exam_context.exam_name,
                "oictionary": data,
                "paginators": paginator,
                "active": key,
                "paper_list": paper,
            }

        if paper:

            url = await ExamCreatePage.insurt_exam_preferences_on_database(
                exam_context.exam_name, exam_context.exam_meta, exam_context.exam_qsto
            )

            ExamCacheMemory.remove(entry)
            return {"submit": True, "jump": url}

        return {"data": None}

    @staticmethod
    async def update_question_submit(entry, exam_context, questions, oictionary):

        if not exam_context:
            return False

        key = next(
            (k for k, v in exam_context.exam_meta.items() if set(v) == set(oictionary)),
            None,
        )

        if not key:
            return False

        _, selected, _ = ExamCreatePage.extract_missing_key_and_ids(
            exam_context.exam_qsto, exam_context.exam_meta
        )

        start = len(selected) + 1

        for index, item in enumerate(questions):
            item["sno"] = start + index

        exam_context.exam_qsto[key] = questions
        await ExamCacheMemory.add(entry, exam_context)

        return True

    @staticmethod
    async def create(request_search):

        entry = request_search.get("entry")
        encoded = request_search.get("tn")

        try:
            exam_name = base64.b64decode(encoded).decode() if encoded else None
        except Exception:
            exam_name = None

        create_exam = CreateExam()
        await create_exam.load()

        exam_context = await ExamCacheMemory.get(entry)
        print("//////////", exam_context)

        if create_exam.question_submit:
            await ExamCreatePage.update_question_submit(
                entry, exam_context, create_exam.questions, create_exam.oictionary
            )
            return await ExamCreatePage.insurt_exam_question(exam_context, entry)

        if entry:
            return await ExamCreatePage.insurt_exam_question(exam_context, entry)

        if create_exam.examPreferences and exam_name and exam_context is None:

            meta = {}
            qsto = {}

            for index, value in enumerate(create_exam.examPreferences, 1):

                key = f"pe{index}"
                meta[key] = value
                qsto[key] = None

            exam_context = ExamContext(exam_name, meta, qsto)
            entry = await ExamCacheMemory.add(entry, exam_context)

            return {"jump": f"/exam/r/create?entry={entry}"}

        if exam_name:

            if create_exam.inte:

                category = await ExamCreatePage.getCategoryBySubject(create_exam.inte)

                return {"category": category, "exam_name": exam_name}

            subject, category = await build_subject_category()

            return {
                "__ac": 111,
                "exam_name": exam_name,
                "subjects": subject,
                "category": category,
            }

        return {"__ac": 110, "exam_name": exam_name, "result": exam_category}
