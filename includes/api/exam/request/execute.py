from includes.api.exam.stlinks import StLinksHendlar
from includes.core.globals.entry import app_context
from includes.api.exam.index import Exam
from includes.api.exam.controller import ExamController
from includes.api.exam.student import RecordType, Student
from includes.api.exam.results.results_conducted import IS_RESULTS

from typing import Any
from dataclasses import dataclass

from includes.utils.utils import get_post_value, json_response


@dataclass
class RequestObject:
    requestKey: int = None
    actionKey: int = None
    action: str = None
    payload: Any = None
    moreData: Any = None


def g(lst, i):
    return lst[i] if isinstance(lst, list) and i < len(lst) else None


def parse_request(data):
    action = g(data, 1)
    info = g(action, 1)

    return RequestObject(
        requestKey=g(data, 0),
        actionKey=g(action, 0),
        action=g(info, 0),
        payload=g(info, 1),
        moreData=g(info, 2),
    )


async def updateHandle(exam_id: int, data: RequestObject, teacher_profile):

    if data.actionKey == 5608:
        await Exam.update(exam_id, data.payload)
        if data.action != True:
            return json_response({"update": True})

    return {}


async def requestHandle(exam_id: int, data: RequestObject, teacher_profile):

    if data.actionKey == 203 and isinstance(data.moreData, int):
        user_id, rollno = data.payload

        if user_id and data.action == "dExam":
            data = await Exam.delete(data.moreData, user_id)
            return json_response(data)

        if not rollno:
            return json_response({"message": "Please enter your Roll Number"})

        if data.action == "qStudent":
            data = await ExamController.search_student(rollno)
            return json_response(data)

        actions = {
            112: StLinksHendlar.add_student,
            113: StLinksHendlar.update_student,
            114: StLinksHendlar.block_student,
            115: StLinksHendlar.unblock_student,
            116: StLinksHendlar.delete_student,
        }

        if handler := actions.get(data.moreData):
            return json_response(
                await handler(
                    exam_category=user_id,
                    strollno=rollno,
                    teacher=teacher_profile,
                )
            )

        exam_query = await Exam.get(data.moreData)
        if exam_query and data.action == "addStudent":
            return json_response(
                await ExamController.request_add(
                    data.moreData, user_id, rollno, exam_query.teacher_id
                )
            )

    exam_query = await Exam.get(exam_id)
    if exam_query is None:
        return json_response({"message": "Invalid meta data", "error": "invalid_meta1"})

    if data.actionKey == 203:
        user_id, rollno = data.payload

        # Validate basic data
        if not exam_id or not data.action or not user_id:
            return json_response(
                {"message": "Invalid meta data", "error": "invalid_meta2"}
            )

        # ----- REMOVE USER FROM EXAM -----
        print("action=>", data.action)

        if data.action in ["unblock", "add", "accept"]:
            return json_response(await ExamController.request_accept(exam_id, user_id))

        elif data.action == "reject":
            return json_response(await ExamController.request_reject(exam_id, user_id))

        elif data.action == "delete":
            return json_response(await ExamController.request_delete(exam_id, user_id))

        elif data.action == "block":
            return json_response(await ExamController.request_block(exam_id, user_id))

        elif data.action == "remove":
            return json_response(await ExamController.remove_to_exam(exam_id, user_id))

        elif data.action == "result":
            record = await Student.get_by_exam(rollno, exam_id, RecordType.INVIGILATOR)
            result_data = await IS_RESULTS.get_result(record, True)
            return json_response(result_data)

        else:
            return json_response(
                {"message": "Invalid meta data", "error": "invalid_meta3"}
            )

    # Fallback if code != 203
    # return await searchStudent(data.action)


async def handle_exam_requests(exam_id=None, teacher_profile=None):

    request_handlers = {300: requestHandle, 302: updateHandle}

    responses = []

    for request in await get_post_value(True, []):
        request_data = parse_request(request)
        handler = request_handlers.get(request_data.requestKey)

        if not callable(handler):
            responses.append(
                {
                    "error": "InvalidRequestKey",
                    "message": f"Unsupported RequestKey: '{request_data.requestKey}'.",
                }
            )
            continue

        responses.append(await handler(exam_id, request_data, teacher_profile))

    return None if not responses else responses[0] if len(responses) == 1 else responses
