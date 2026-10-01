import asyncio

from includes.api.exam.student import RecordType, Student
from includes.core.globals.entry import app_context
from includes.utils.utils import json_response


class StudentExamPanel:

    @staticmethod
    async def dashboard(params):
        page = int(params.get("page", 0))
        list_session = params.get("ls", "practice")

        student = await app_context.setting.member()
        roll_no = student["roll_no"]

        student_task = Student.get_submission_counts(
            roll_no,
            RecordType.STUDENT,
            page=page,
            limit=10,
            list_getter=(list_session == "practice"),
        )

        invigilator_task = Student.get_submission_counts(
            roll_no,
            RecordType.INVIGILATOR,
            page=page,
            limit=10,
            list_getter=(list_session == "examiner_conducted"),
        )

        (
            (practice_list, practice_pagination, s_daily, s_monthly, s_yearly, s_total),
            (examiner_list, examiner_pagination, i_daily, i_monthly, i_yearly, i_total),
        ) = await asyncio.gather(student_task, invigilator_task)

        return {
            "__ac": 121,
            "student": {
                "roll_no": roll_no,
                "name": student.get("name"),
                "img": student.get("img"),
                "username": student.get("username"),
                "biography": student.get("biography"),
                "reg_no": student.get("reg_no"),
            },
            "account_type": "Free",
            "join": i_total,
            "self": s_total,
            "today": s_daily + i_daily,
            "this_month": s_monthly + i_monthly,
            "this_year": s_yearly + i_yearly,
            "all_time": s_total + i_total,
            "pagination": practice_pagination or examiner_pagination,
            "practice": practice_list,
            "examiner_conducted": examiner_list,
        }

    @staticmethod
    async def account(path, params):
        data = await StudentExamPanel.dashboard(params)
        return json_response(data)
