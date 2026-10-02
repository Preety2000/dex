from includes.api.exam.controller import ExamController
from includes.api.exam.session.ev import ExamEventManager
from includes.api.exam.teacher import Teachers
from includes.core.globals.entry import app_context

from includes.api.exam.index import Exam
from includes.utils.exm import get_exam_id
from includes.api.exam.metadata import exam_setting_setter, build_settings_page
from includes.utils.utils import get_post_value, json_response


class ExamIndexPage:

    @staticmethod
    async def get_exam(exam_id):
        response = await Exam.get_with_details(exam_id)
        await ExamController.get_exam_summary(exam_id, response)
        return response

    @staticmethod
    async def index(path, request_search):
        id = request_search.get("id")
        page = int(request_search.get("page", 0))
        jump = request_search.get("Jump")
        route = request_search.get("_request_type")
        exam_id = get_exam_id(id)
        language = await app_context.setting.get("language", "English")

        if exam_id:
            if route == "c7b4e436-ab36-4a93-834-565159552bdc":
                exam_query = await Exam.get(exam_id)

                update, exam_query = await exam_setting_setter(exam_query)
                for i in ["start_timestamp", "publish_timestamp"]:
                    value = await get_post_value(i)
                    if value and int(value):
                        update = True
                        setattr(exam_query, i, int(value))

                if update is True:
                    setattr(
                        exam_query,
                        "exam_category",
                        await get_post_value("exam_category", "any"),
                    )
                    setattr(
                        exam_query,
                        "notification",
                        True if await get_post_value("notification") == "ON" else False,
                    )
                    exam_query = await Exam._update(exam_query)
                    if jump:
                        return {"jump": f"{path}?id={id}"}

                exam_query.teacher_record = await Teachers.get(exam_query.teacher_id)
                return await build_settings_page(language, exam_query)

            response = {"__ac": 113, "query": await ExamIndexPage.get_exam(exam_id)}

            await ExamEventManager.start_exam_session(exam_id)

            if response["query"]:
                response["route"] = "examListSession"
            else:
                response.jump = path

            return response

        else:
            dbList, paginators, results = await Exam.get_lists(
                await app_context.setting.member("id"), 10, page
            )
            return {
                "__ac": 113,
                "list": dbList,
                "paginators": paginators,
                "results": results,
                "route": "list",
            }
