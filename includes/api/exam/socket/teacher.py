import time
import re

from sqlalchemy import asc, desc
from includes.api.exam.controller import ExamController, get_exam_request_session
from includes.utils.exm import get_exam_id
from includes.api.exam.request.exam_setting import CreateStore
from includes.api.exam.session.ev import ExamEventManager
from includes.db.connection import active_exam_db
from includes.db.dataclass import ExamRqStatus
from includes.db.models.db_exam import ExamRequestSession


def get_exam_ids(detail):
    match = re.search(r"t=([^&]*)", detail)
    return get_exam_id(match.group(1)) if match else None


class ExamSetting:

    @staticmethod
    def get_exam_request_start_method(teacher_id):
        return True


# date_asc: "Oldest First",
# date_desc: "Newest First",
# name_asc: "Student Name (A–Z)",
# name_desc: "Student Name (Z–A)",
# roll_no_asc: "Roll No (Ascending)",
# roll_no_desc: "Roll No (Descending)",


def build_order_by(key):
    try:
        field, direction = key.rsplit("_", 1)
        column = {
            "name": ExamRequestSession.student_name,
            "roll_no": ExamRequestSession.roll_no,
            "date": ExamRequestSession.started_at,
        }[field]

    except (ValueError, KeyError):
        return asc(ExamRequestSession.started_at)  # default

    return (asc if direction == "asc" else desc)(column)


class requestRoute:

    @staticmethod
    async def get_exam_requests(
        exam_id: int, payload: list, joined_status: list, use_filter: callable = None
    ) -> dict:
        offset, limit = payload
        db = await active_exam_db()

        query = db.query(ExamRequestSession).filter(
            ExamRequestSession.exam_id == exam_id,
            ExamRequestSession.joined_status.in_(joined_status),
        )

        query = (
            use_filter(query)
            if callable(use_filter)
            else query.order_by(desc(ExamRequestSession.started_at))
        )

        total = query.count()
        students, records = {}, []

        for row in query.offset(offset).limit(limit).all():
            students[row.id] = [row.student_name, row.roll_no, row.profile_image]
            records.append(get_exam_request_session(row))

        return {"record": records, "students": students, "srs_tr": total}

    @staticmethod
    async def blocked_student_list(
        *,
        exam_id: int = None,
        payload: list = list,
        use_filter: bool = None,
    ):

        def apply_request_filters(query):
            req = CreateStore.get()
            reqOrder, reqView = req.get("reqOrder"), req.get("reqView")
            return query.order_by(build_order_by(reqOrder)) if reqOrder else query

        return await requestRoute.get_exam_requests(
            exam_id,
            payload,
            [ExamRqStatus.BLOCK_IN_EXAM],
            apply_request_filters if use_filter else None,
        )

    @staticmethod
    async def remove_student_list(
        *,
        exam_id: int = None,
        payload: list = list,
        use_filter: bool = None,
    ):

        def apply_request_filters(query):
            req = CreateStore.get()
            reqOrder, reqView = req.get("reqOrder"), req.get("reqView")
            return query.order_by(build_order_by(reqOrder)) if reqOrder else query

        return await requestRoute.get_exam_requests(
            exam_id,
            payload,
            [ExamRqStatus.STUDENT_REMOVED_FROM_EXAM],
            apply_request_filters if use_filter else None,
        )

    @staticmethod
    async def studentReqsAptAll(exam_id, method: str):
        db = await active_exam_db()

        query = db.query(ExamRequestSession).filter(
            ExamRequestSession.exam_id == exam_id,
            ExamRequestSession.joined_status == ExamRqStatus.STUDENT_REQUEST_SEND,
        )

        method = method.replace(" ", "")

        if method == "AcceptAll":
            return {
                "result_count": query.count(),
                "results": [
                    await ExamController.request_accept(exam_id, record.id)
                    for record in query.all()
                ],
            }
        if method == "RejectAll":
            return {
                "result_count": query.count(),
                "results": [
                    await ExamController.request_reject(exam_id, record.id)
                    for record in query.all()
                ],
            }
        if method == "DeleteAll":
            return {
                "result_count": query.count(),
                "results": [
                    await ExamController.request_delete(exam_id, record.id)
                    for record in query.all()
                ],
            }

        return {}

    @staticmethod
    async def studentReqs(exam_id, payload, use_filter=None):
        def apply_request_filters(query):
            req = CreateStore.get()
            req_order, req_view = req.get("reqOrder"), req.get("reqView")

            if req_view == "rejected":
                query = query.filter(
                    ExamRequestSession.joined_status == ExamRqStatus.REQUEST_REJECTED
                )

            return query.order_by(build_order_by(req_order)) if req_order else query

        return await requestRoute.get_exam_requests(
            exam_id,
            payload,
            [ExamRqStatus.STUDENT_REQUEST_SEND, ExamRqStatus.REQUEST_REJECTED],
            apply_request_filters if use_filter else None,
        )


async def exam_control_socket_handler(detail, incoming):
    start = time.perf_counter()

    exam_id = get_exam_ids(detail)
    if exam_id is None:
        return

    if incoming:
        log = incoming.get("log")

        if log:
            return {"status": True}

        payload = incoming.get("payload")
        req_route = incoming.get("reqRoute")
        use_filter = incoming.get("useFilter")
        request_key = incoming.get("request_key")

        if not req_route:
            return {"error": "Missing reqRoute"}

        if req_route == "studentReqs":
            data = await requestRoute.studentReqs(exam_id, payload, use_filter)

        if req_route == "stuReqsBlk":
            return await requestRoute.blocked_student_list(
                payload=payload, exam_id=exam_id, use_filter=use_filter
            )

        if req_route == "stuReqsRemv":
            return await requestRoute.remove_student_list(
                payload=payload, exam_id=exam_id, use_filter=use_filter
            )

        if req_route == "reqApprAct":
            data = await requestRoute.studentReqsAptAll(exam_id, payload)

        data["request_key"] = request_key

        end = time.perf_counter()
        print(f"Time taken: {end - start:.4f} seconds")

        return data

    await ExamEventManager.start_exam_session(exam_id)
    return await ExamEventManager.fetch_next_exam_event(exam_id)
