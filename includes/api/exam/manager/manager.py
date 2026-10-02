from includes.api.exam.stlinks import StLinksHendlar
from includes.core.globals.entry import app_context
from includes.db.models.db_exam import _TeacherProfile
from includes.schemas.subject import ClassSubject
from includes.src.request import RequestContext
from includes.api.exam.index import Exam
from includes.api.exam.router import ReqRoute
from includes.utils.exm import get_exam_id
from includes.api.exam.pages.index import ExamIndexPage
from includes.api.exam.pages.create import ExamCreatePage
from includes.api.exam.manager.practice import SELF_EXAM_MANAGER
from includes.api.exam.request.execute import handle_exam_requests
from includes.api.exam.controller import ExamController
from includes.api.exam.processor import ExamtProcessor

from includes.api.exam.teacher import Teachers, check_teacher_authorization
from includes.api.exam.pages.student import StudentExamPanel
from includes.api.exam.pages.dashboard import ExamDashboard
from includes.api.exam.metadata import (
    exam_setting_setter,
    build_settings_page,
    get_selected_classes,
)
from includes.utils.utils import get_post_value, json_response


class API_EXAM_MANAGER:
    def __init__(self):
        self.ex_keys_ids = None
        self.examController = None

    async def test_manager(self):

        # Safely extract referer, path, and params
        referer = getattr(app_context.request, "referer")
        if not isinstance(referer, RequestContext):
            print("Invalid referer format:", referer)
            return None

        """Active exam database"""
        await app_context.db.configure_exam()

        is_authorized = referer.subresource == "r"
        teacher_profile = await check_teacher_authorization(is_authorized)

        # _TeacherProfile

        # If verification route → return immediately
        if is_authorized and isinstance(teacher_profile, (dict, str, list, int)):
            update = await get_post_value("update")
            if update and all(update):
                return update

            return teacher_profile

        exam_id = get_exam_id(referer.params.get("id"))
        req_route = await get_post_value("reqRoute")

        if req_route:
            return json_response(
                await ReqRoute(roots=req_route, exam_id=exam_id).execute(is_authorized)
            )

        if is_authorized:
            # Handle exam-based requests
            if result := await handle_exam_requests(exam_id, teacher_profile):
                return result

            return json_response(
                await self.dashboard_roots(
                    referer.path, referer.params, teacher_profile
                )
            )

        # Final fallback → root handling
        return await self.roots(referer.path, referer.params)

    async def dashboard_roots(self, path, params, teacher):
        response = {}
        language = await app_context.setting.get("language")

        if path == "/exam/r/setting":
            teacher_id = await app_context.setting.member("id")
            teacher_session = await Teachers.get(teacher_id)

            update, teacher_session = await exam_setting_setter(teacher_session)
            for name in ["biography", "img", "signature", "name", "exam_category"]:
                value = await get_post_value(name)
                if value and str(value).strip():
                    update = True
                    setattr(teacher_session, name, value)

            if update is True:
                teacher_session = await Teachers.update(teacher_session)
                return await build_settings_page(language, teacher_session, True)

            return await build_settings_page(language, teacher_session)

        elif path == "/exam/r/dashboard":
            return await ExamDashboard.get_dashboard_data()

        elif path == "/exam/r/student":
            return await self.students(teacher, params)

        elif path == "/exam/r/create":
            return await ExamCreatePage.create(params)

        elif path == "/exam/r/index":
            return await ExamIndexPage.index(path, params)

        if not response.get("__ac"):
            response["__ac"] = 103

        return response

    async def roots(self, path, params):
        response = {}
        if path == "/exam":
            ep = ExamtProcessor(await app_context.setting.member())
            return await ep.handle_exam_request(path, params)

        elif path == "/exam/create":
            self_exam_manager = SELF_EXAM_MANAGER()
            return await self_exam_manager.index(response)

        elif path.startswith("/exam/dashboard"):
            return await StudentExamPanel.account(
                path.replace("/exam/dashboard", ""), params
            )

        return json_response(response)

    async def getCategoryBySubject(self, query):
        count, _subject = query
        category = [
            {"subject": _subject, "count": 1000, "entry": ["default", "All Category"]}
        ]
        get_subject = await ClassSubject.get_with_terms()

        if not _subject:
            subjects = ["All Subject"]
            for item in get_subject:
                if (
                    max(
                        (i.get("mcq_count", 0) for i in (item.get("terms") or [])),
                        default=0,
                    )
                    < 10
                ):
                    continue

                subjects.append(item.get("name"))

            return subjects

        def quit(terms):
            for itex in terms:
                mcq_count = itex.get("mcq_count")
                if mcq_count > 0 and mcq_count >= count:
                    array_query = {
                        "subject": subject_name,
                        "count": itex.get("mcq_count"),
                        "entry": [itex.get("slug"), itex.get("name")],
                    }
                    category.append(array_query)

        for item in get_subject:
            subject_name = item.get("name")
            if _subject != "All Subject" and subject_name != _subject:
                continue

            quit(item.get("terms") or [])

        return category

    async def students(self, teacher: _TeacherProfile, params):
        lists, pagination, total = await StLinksHendlar.get_list(teacher)
        return {
            "__ac": 104,
            "list": lists,
            "total": total,
            "pagination": pagination,
            "exam_category": get_selected_classes(teacher.exam_category),
        }

    @staticmethod
    async def get(exam_id: int):
        """Fetch detailed information about an exam by its ID."""

        response = await Exam.get_with_details(exam_id)
        await ExamController.get_exam_summary(exam_id, response)
        return response

    def delete(self, user_id: int):
        # exam = self.query.filter_by(user_id=user_id).first()
        # if not exam:
        #     return False  # Or raise an error

        # self.database.session.delete(exam)
        # self.database.session.commit()
        return True

    async def checkRequest(self, request_mode: str):
        if request_mode == "openAccessRequests":
            return True

        if request_mode == "approvalRequired":
            return False

        if request_mode == "directAccess":
            return False

        return False
