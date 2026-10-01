# 5061: Socket event to add all join list
# 5062: Socket event to add a request to join an exam
# 5063: Socket event to remove a request to join an exam
# 5064: Socket event to start an exam session
# 5065: Socket event to end an exam session
# 5066: Socket event to submit an exam answer
# 5067: Socket event to update an exam answer
# 5068: Socket event to fetch exam results
# 5069: Socket event to notify exam status change
# 5070: Socket event to cancel an exam session

# Request handler

import os
from sqlalchemy import asc, desc
from includes.api.exam.student import RecordType, Student
from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.db.dataclass import ExamRqStatus
from includes.db.models.db_exam import _ExamRequestSession, ExamRequestSession
from includes.api.exam.session.ev import ExamEventManager
from includes.api.exam.socket.student_req import StudentRequestSession
from includes.schemas.cache.member import MemberCache
from includes.utils.utils import json_response


async def get_exam_setting() -> dict[str, int]:

    keys = ("id", "exam_view", "request_view")
    parts = (app_context.cookie.get("_cf_est") or "").split("/")

    return {
        k: max(len(parts[i]) - 6, 0) if i < len(parts) else 0
        for i, k in enumerate(keys)
    }


def build_update_request(id, code, update_data):
    return {
        "request_id": id,
        "update_code": code,
        "payload": (
            {
                "roll_no": update_data.roll_no,
                "student_name": update_data.student_name,
            }
            if update_data
            else None
        ),
    }


def get_exam_request_session(record: _ExamRequestSession):
    return [
        record.id,
        [
            record.joined_status,
            record.total_request,
            record.total_exam_joins,
            record.request_timestamps[-1] if record.request_timestamps else None,
            record.join_timestamps,
            record.leave_timestamps,
            record.is_joined,
            record.is_re_requested,
        ],
    ]


async def push_exam_event_by_joined_status(record: _ExamRequestSession):

    print("=>>record.joined_status", record.joined_status)

    summary = await ExamController.get_exam_summary(
        record.exam_id, {}, record=record, only_count=True
    )

    await ExamEventManager.push_exam_event(
        record.exam_id,
        [
            5060,
            {
                **summary,
                ExamRqStatus(record.joined_status).name: [
                    get_exam_request_session(record)
                ],
            },
        ],
    )


class ExamController:

    @staticmethod
    async def search_student(rollno: int):
        if rollno is None or len(str(rollno).strip()) < 8:
            return {
                "message": "Invalid roll number, please check.",
                "error_type": "invalid_student_rollno",
            }

        student = await MemberCache.getrollnumber(rollno)
        if not student:
            return {
                "message": "No student found with the provided roll number.",
                "error_type": "student_not_found",
            }

        return {
            "user_id": _Security.number_encode(int(student.get("id"))),
            "img": student.get("img"),
            "name": student.get("name"),
            "reg_no": student.get("reg_no"),
            "rollno": student.get("roll_no"),
            "username": student.get("username"),
        }

    @staticmethod
    async def request_add(exam_id, user_id, roll_no, teacher_id):

        student = await MemberCache.getrollnumber(roll_no)
        if not student:
            return {
                "message": "Student not found.",
                "error_type": "student_not_found",
            }

        if user_id != _Security.number_encode(int(student.get("id"))):
            return {
                "message": "Student verification failed.",
                "error_type": "student_verification_failed",
            }

        row = (
            app_context.db.query(ExamRequestSession)
            .filter_by(
                roll_no=int(roll_no),
                exam_id=int(exam_id),
            )
            .first()
        )

        if row is None:
            row = ExamRequestSession(
                exam_id=exam_id,
                teacher_id=teacher_id,
                roll_no=roll_no,
                student_name=student.get("name"),
                profile_image=student.get("img"),
                is_joined=True,
                is_re_requested=False,
                total_exam_joins=0,
                total_request=1,
                request_timestamps=[],
                connect_key=os.urandom(5).hex(),
                joined_status=ExamRqStatus.STUDENT_PENDING_EXAM,
            )

            app_context.db.add(row)

        else:
            if row.joined_status in [
                ExamRqStatus.STUDENT_PENDING_EXAM,
                ExamRqStatus.STUDENT_JOINED_EXAM,
                ExamRqStatus.STUDENT_LEFT_EXAM,
            ]:
                return {
                    "message": "A join request for this student is already exists.",
                    "error_type": "duplicate_student_request",
                }

            # Re-request
            row.joined_status = ExamRqStatus.STUDENT_PENDING_EXAM
            row.is_re_requested = True
            row.total_request += 1

        # Save changes
        app_context.db.commit()
        app_context.db.refresh(row)

        summary = await ExamController.get_exam_summary(
            exam_id, {}, record=row, only_count=True
        )
        await ExamEventManager.push_exam_event(
            exam_id,
            [
                5060,
                {
                    **summary,
                    "STUDENT_JOINED_EXAM": [get_exam_request_session(row)],
                },
            ],
        )

        return {"message": "✅ Student has been added to the exam successfully."}

    @staticmethod
    async def request_accept(exam_id: int, id: str):
        async def bind(record, session):
            record.joined_status = ExamRqStatus.STUDENT_PENDING_EXAM
            return record

        update_data = await StudentRequestSession.update(bind, id=id)
        if update_data:
            summary = await ExamController.get_exam_summary(
                exam_id, {}, record=update_data, only_count=True
            )
            await ExamEventManager.push_exam_event(
                exam_id,
                [
                    5060,
                    {
                        "students": {
                            update_data.id: [
                                update_data.student_name,
                                update_data.roll_no,
                                update_data.profile_image,
                            ]
                        },
                        **summary,
                        "STUDENT_JOINED_EXAM": [get_exam_request_session(update_data)],
                    },
                ],
            )

        return build_update_request(id, 1, update_data)

    @staticmethod
    async def request_reject(exam_id: int, id: str):
        async def bind(record, query):
            record.joined_status = ExamRqStatus.REQUEST_REJECTED
            return record

        update_data = await StudentRequestSession.update(bind, id=id)
        if update_data:
            await ExamEventManager.push_exam_event(
                exam_id,
                [5060, {"REQUEST_REJECTED": [get_exam_request_session(update_data)]}],
            )

        return build_update_request(id, 2, update_data)

    @staticmethod
    async def request_delete(exam_id: int, id: str):
        update_data = await StudentRequestSession.delete(id=id, exam_id=exam_id)
        return build_update_request(id, 3, update_data)

    @staticmethod
    async def remove_to_exam(exam_id: int, id: str):
        async def bind(record, query):
            record.joined_status = ExamRqStatus.STUDENT_REMOVED_FROM_EXAM
            return record

        update_data = await StudentRequestSession.update(bind, id=id)
        if update_data:
            summary = await ExamController.get_exam_summary(
                update_data.exam_id, {}, record=update_data, only_count=True
            )
            await ExamEventManager.push_exam_event(
                exam_id,
                [
                    5060,
                    {
                        **summary,
                        "STUDENT_REMOVED_FROM_EXAM": [
                            get_exam_request_session(update_data)
                        ],
                    },
                ],
            )

        return build_update_request(id, 4, update_data)

    @staticmethod
    async def request_block(exam_id: int, id: str):

        async def bind(record, query):
            record.joined_status = ExamRqStatus.BLOCK_IN_EXAM
            return record

        update_data = await StudentRequestSession.update(bind, id=id)
        if update_data:
            summary = await ExamController.get_exam_summary(
                update_data.exam_id, {}, record=update_data, only_count=True
            )
            await ExamEventManager.push_exam_event(
                exam_id,
                [
                    5060,
                    {
                        **summary,
                        "STUDENT_REMOVED_FROM_EXAM": [
                            get_exam_request_session(update_data)
                        ],
                    },
                ],
            )

        return build_update_request(id, 5, update_data)

    @staticmethod
    async def get_exam_summary(
        exam_id: int, returns: dict, *, record=None, only_count=None
    ):
        returns["students"] = {}
        setting = await get_exam_setting()
        query = app_context.db.query(ExamRequestSession).filter(
            ExamRequestSession.exam_id == exam_id
        )

        def get_joined_statuses_data(statuses, order_by=None):
            f_query = query.filter(ExamRequestSession.joined_status.in_(statuses))
            return f_query.order_by(order_by) if order_by is not None else f_query

        def add_student(record):
            returns["students"][record.id] = [
                record.student_name,
                record.roll_no,
                record.profile_image,
            ]

        for status_key, query in [
            [
                "STUDENT_REQUEST_SEND",
                get_joined_statuses_data(
                    [ExamRqStatus.STUDENT_REQUEST_SEND],
                    desc(ExamRequestSession.started_at),
                ),
            ],
            [
                "STUDENT_JOINED_EXAM",
                get_joined_statuses_data(
                    [
                        ExamRqStatus.STUDENT_JOINED_EXAM,
                        ExamRqStatus.STUDENT_LEFT_EXAM,
                        ExamRqStatus.STUDENT_PENDING_EXAM,
                    ]
                ),
            ],
            [
                "STUDENT_COMPLETED_EXAM",
                get_joined_statuses_data([ExamRqStatus.STUDENT_COMPLETED_EXAM]),
            ],
        ]:

            returns[f"{status_key}_COUNT"] = query.count()
            if record:
                add_student(record)

            if not only_count is True:
                if status_key not in returns:
                    returns[status_key] = []

                for record in query.limit(30).all():
                    add_student(record)
                    data = get_exam_request_session(record)

                    if "STUDENT_COMPLETED_EXAM" == status_key and (
                        rq_sesion := await Student.get_by_exam(
                            roll_no=record.roll_no,
                            exam_id=exam_id,
                            record_type=RecordType.INVIGILATOR,
                        )
                    ):
                        data.append(rq_sesion.allmarks)

                    returns[status_key].append(data)

        return returns
