from includes.api.exam.student import RecordType, Student
from includes.utils.exm import get_exam_id
from includes.api.exam.results.results_conducted import IS_RESULTS
from includes.core.globals.entry import app_context
from includes.src.request import Request
import base64
import json

from includes.core.security import _Security


def decode(token):
    if not token:
        return None
    try:
        token += "=" * ((4 - len(token) % 4) % 4)
        decoded = base64.b64decode(token).decode("utf-8")
        return json.loads(decoded)
    except Exception as err:
        print("Invalid token:", err)
        return None


class QS:

    @staticmethod
    async def index(request: Request, resource, subresource, templates):
        _id = request.query_params.get("id")
        [root, b, c, d] = decode(resource)

        # try:
        if root == "result":
            exam_id = get_exam_id(d)
            record = await Student.get_by_exam(c, exam_id, RecordType.INVIGILATOR)

            if record and _id == "t0f5s":
                result_no, lists, student = await IS_RESULTS.get_ans_seet(record)

                template_context = {
                    "lists": lists,
                    "result_no": result_no,
                    "sname": student.get("name"),
                    "svg": app_context.svg_lists,
                    "config": app_context.config,
                    "app_context": app_context,
                    "function": app_context.function,
                    "request": request,
                    "response": request.state.response,
                    "security": _Security,
                }
                return templates.TemplateResponse(
                    "qs/ansseet.html",
                    {**template_context, "request": request},
                    status_code=200,
                )

            is_result = IS_RESULTS(request)
            result_data = await is_result.get_result(record, True, True)
            if result_data:
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
                    "paper": result_data[2],
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
                template_context = {
                    **result,
                    "svg": app_context.svg_lists,
                    "config": app_context.config,
                    "app_context": app_context,
                    "function": app_context.function,
                    "request": request,
                    "response": request.state.response,
                    "security": _Security,
                }
                return templates.TemplateResponse(
                    f"qs/result.html",
                    {**template_context, "request": request},
                    status_code=200,
                )
        # except:
        #     return "Error code: Ex_85858"

        return templates.TemplateResponse(
            f"qs/error.html", {"request": request}, status_code=403
        )
