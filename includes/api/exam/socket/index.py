import asyncio
import copy
import json
import random
from attr import dataclass
from enum import IntEnum

from includes.api.exam.controller import (
    get_exam_request_session,
    push_exam_event_by_joined_status,
)
from includes.api.exam.index import Exam, get_exam_dick
from includes.api.exam.metadata import requestTimeOutMessage, testSubmitted
from includes.api.exam.session.es import ES
from includes.api.exam.session.ev import ExamEventManager
from includes.api.exam.socket.student_req import StudentRequestSession
from includes.api.exam.socket.teacher import exam_control_socket_handler
from includes.api.exam.student import RecordType, Student
from includes.api.router import DynamicSokitURLRoute
from includes.core.globals.coreutils import generate_unique_uuid
from includes.core.globals.entry import app_context
from includes.database.dataclass.dataclass import ExamRqStatus
from includes.database.models.db_exam import ExamRequestSession, _ExamDetails, _ExamRecord
from includes.database.models.utils import TimeStamp
from includes.utils.exm import (
    block_exam_message,
    calculate_exam_stats,
    exam_not_started_message,
    exam_submitted_message,
    exam_timeout_message,
    get_invalid_activity_error,
    get_session_key_and_exam_key,
    get_waiting_message,
    is_expired_exam,
    remove_exam_message,
    time_until,
)

ACTIVE_STUDENTS = {}


class ExamType(IntEnum):
    PRACTICE = 3
    TEACHER_ASSIGNED = 4


class SessionStatus(IntEnum):
    INITIALIZED = 0
    CONNECTED = 1
    DISCONNECTED = 2
    CLOSED = 3
    EXPIRED = 4


@dataclass
class SocketSession:
    status: SessionStatus
    hx_key: str
    session_id: str
    connection_id: str


def get_request_session(websocket, request) -> SocketSession:
    """Retrieve or initialize socket session for websocket."""
    if not hasattr(websocket, "request_session"):
        session_id, exam_key, connection_id = get_session_key_and_exam_key(request)

        websocket.request_session = SocketSession(
            status=SessionStatus.INITIALIZED,
            hx_key=exam_key,
            session_id=session_id,
            connection_id=connection_id,
        )

    return websocket.request_session


def is_valid_session(roll_no: str, socket_ses: SocketSession, incoming: dict) -> bool:
    """
    Validate incoming request against stored session.
    Returns True if valid, False if invalid session state detected.
    """
    request_key = incoming.get("key") if isinstance(incoming, dict) else None
    session_key, _ = ES.get(roll_no, (None, None))

    if not session_key:
        return True

    # Check if session key matches active websocket session
    if session_key != socket_ses.session_id:
        return False

    if request_key and session_key != request_key:
        return False

    return True


def format_close_response(response_content):
    """Utility to format code 116 session close payloads."""
    return {"__ac": {116: {"session": "close", "content": response_content}}}


async def init_exam_session(
    ser_st: ExamRequestSession, exam_details: _ExamDetails
) -> ExamRequestSession | None:
    """Initialize student exam record and randomize question options."""
    async def callback(record, q):
        record.has_key = generate_unique_uuid()
        record.srec_kry = await Student.insert(
            ser_st.roll_no,
            getattr(exam_details, "code", exam_details.id),
            {
                k: [
                    [q["id"], random.sample(q["options"], len(q["options"])), None]
                    for q in qs
                ]
                for k, qs in exam_details.questions.items()
            },
        )
        record.started_at = exam_details.start_timestamp
        return record

    return await StudentRequestSession.update(callback, id=ser_st.id)


class ExamSocket:
    def __init__(self, request):
        self.request = request
        self.websocket = request
        self.countdown = False
        self.temp_store = getattr(self.websocket.state, "tamp", {})
        self.websocket.state.tamp = self.temp_store

    async def incoming_data(self, incoming):
        if not incoming:
            return {}

        if isinstance(incoming, (list, dict)):
            return incoming

        try:
            return json.loads(incoming)
        except (json.JSONDecodeError, TypeError):
            return {}

    async def get_exam_data(
        self, socket_ses: SocketSession, session_query, exm, incoming
    ):
        returns = copy.deepcopy(await get_exam_dick(exm, True))

        just_timestamp = TimeStamp.now_timestamp()
        start_timestamp = returns["start_timestamp"]
        end_timestamp = returns["endTime"]

        # Strip answers from questions payload
        for questions in returns["questions"].values():
            for q in questions:
                q.pop("options", None)
                q.pop("correct_answer", None)

        target_time, total_seconds = time_until(start_timestamp)
        if total_seconds == 180:
            return {}

        if total_seconds > 10:
            if self.temp_store.get("countdown", False) and not incoming:
                return None

            await asyncio.sleep(1)
            self.temp_store["countdown"] = True
            days = total_seconds // (60 * 60 * 24)
            
            if days <= 0:
                return {
                    "__ac": {
                        118: {
                            "just": just_timestamp,
                            "start": start_timestamp,
                            "end": end_timestamp,
                            "content": get_waiting_message(returns["exam_name"]),
                        }
                    }
                }
            return format_close_response(exam_not_started_message(target_time))

        student = self.websocket.state.member
        returns.update({
            "option_name": "कखगघ",
            "stu_img": student.get("img"),
            "reg_no": student.get("reg_no"),
            "roll_no": student.get("roll_no"),
            "stu_name": student.get("name"),
            "position": session_query.position,
            "pe_point": session_query.pe_point,
            "submit": session_query.content,
        })

        await ExamEventManager.update_student_status(
            session_query.exam_id, session_query.roll_no
        )

        socket_ses.status = SessionStatus.CONNECTED
        ACTIVE_STUDENTS[session_query.roll_no] = socket_ses.session_id

        return {"__ac": {115: returns}}

    async def get_self_exam_data(self, socket_ses: SocketSession, stu_rec):
        roll_no = self.websocket.state.member.get("roll_no")

        socket_ses.status = SessionStatus.CONNECTED
        ACTIVE_STUDENTS[roll_no] = socket_ses.session_id

        info = stu_rec.ts_info.get("info", [])
        details = stu_rec.ts_info.get("details")
        questions = stu_rec.ts_info.get("questions", {})

        sno = 0
        for q_list in questions.values():
            for q in q_list:
                sno += 1
                q["sno"] = sno

        end_time = stu_rec.timestamp + (info[0] * 60 * 1000) if info else stu_rec.timestamp
        student = self.websocket.state.member

        return {
            "__ac": {
                122: {
                    "exam_name": "Self Online Test Series",
                    "option_name": "कखगघ",
                    "stu_img": student.get("img"),
                    "reg_no": student.get("reg_no"),
                    "stu_name": student.get("name"),
                    "roll_no": student.get("roll_no"),
                    "questions": questions,
                    "details": details,
                    "endTime": end_time,
                    "submit": stu_rec.content,
                    "position": stu_rec.position,
                    "start_timestamp": stu_rec.timestamp,
                    "pe_point": stu_rec.pe_point,
                }
            }
        }

    async def update_exam_status(self, incoming, stu_rec, exm, req_sess):
        iex_value = incoming.get("iex")
        position = incoming.get("position")
        pe_point = incoming.get("pe_point")
        submit = incoming.get("submit")

        if position is not None:
            stu_rec.position = position

        if pe_point is not None:
            stu_rec.pe_point = pe_point

        if isinstance(iex_value, list) and len(iex_value) == 3:
            _, iex, value = iex_value

            if isinstance(iex, int) and value is not None:
                content = dict(getattr(stu_rec, "content", {}))
                for items in content.values():
                    for i, item in enumerate(items):
                        if item and item[0] == value[0]:
                            items[i] = value
                stu_rec.content = content

        async def on_disconnect(record: _ExamRecord = stu_rec):
            record_type = RecordType.INVIGILATOR if exm else RecordType.STUDENT
            return await Student.update(record, record_type)

        self.websocket.state.disconnect_callback["stu_rec_update"] = on_disconnect

        if submit is not None:
            stu_rec.is_submitted = submit
            req_sess.joined_status = ExamRqStatus.STUDENT_COMPLETED_EXAM
            req_sess.leave_timestamps.append(TimeStamp.now_timestamp())
            update_data = await StudentRequestSession.update(req_sess)

            if exm and stu_rec.exam_id == exm.id and update_data:
                update_d = await on_disconnect(stu_rec)
                completed, joined, requests = await StudentRequestSession.get_with_is_joined(stu_rec.exam_id)

                record = get_exam_request_session(update_data)
                record.append(update_d.allmarks)
                await ExamEventManager.push_exam_event(
                    stu_rec.exam_id,
                    [
                        5060,
                        {
                            "students": {
                                req_sess.id: [
                                    req_sess.student_name,
                                    req_sess.roll_no,
                                    req_sess.profile_image,
                                ]
                            },
                            "STUDENT_COMPLETED_EXAM": [record],
                            "STUDENT_REQUEST_SEND_COUNT": requests,
                            "STUDENT_JOINED_EXAM_COUNT": joined,
                            "STUDENT_COMPLETED_EXAM_COUNT": completed,
                        },
                    ],
                )

            self.websocket.state.disconnect_callback.pop("stu_rec_update", None)
            return stu_rec.key

        return None

    async def connect_exam(self, socket_ses: SocketSession):
        """Handles student connection and timeout validation."""
        if not hasattr(self.websocket, "rto"):
            setattr(self.websocket, "rto", TimeStamp.now_timestamp() + 50000)

        request_timeout = getattr(self.websocket, "rto")

        if request_timeout < TimeStamp.now_timestamp():
            return format_close_response(
                requestTimeOutMessage.get("English", "Time’s Up!.")
            )

        roll_no = self.websocket.state.member.get("roll_no")
        ser_st = await StudentRequestSession.connect(roll_no, socket_ses.connection_id)

        if not ser_st:
            return format_close_response(remove_exam_message("/"))

        if ser_st.roll_no != roll_no:
            return None

        if ser_st.joined_status in (
            ExamRqStatus.STUDENT_PENDING_EXAM,
            ExamRqStatus.STUDENT_JOINED_EXAM,
            ExamRqStatus.STUDENT_LEFT_EXAM,
            ExamRqStatus.STUDENT_REMOVED_FROM_EXAM,
        ):
            if getattr(self.websocket, "PEJR", False):
                return

            setattr(self.websocket, "PEJR", True)
            exam_details = await Exam.get(ser_st.exam_id)

            if ser_st.joined_status == ExamRqStatus.STUDENT_REMOVED_FROM_EXAM:
                return {
                    "status": "close",
                    "statusCode": ser_st.joined_status,
                    "content": block_exam_message("/test"),
                }

            record = await init_exam_session(ser_st, exam_details)
            origin = app_context.request.headers.get("origin", "")
            ACTIVE_STUDENTS[roll_no] = socket_ses.session_id

            return {
                "status": "open",
                "infoMessage": "Request accepted",
                "statusCode": ser_st.joined_status,
                "joinLink": f"{origin}/exam?hx={record.has_key}",
            }

        await asyncio.sleep(2)
        return {
            "status": "waiting",
            "request_timeout": request_timeout,
            "request_status": ser_st.joined_status,
            "studentExamSession": str(ser_st),
        }

    async def websocket_handler(self, incoming, roots: DynamicSokitURLRoute):
        incoming = await self.incoming_data(incoming)
        if incoming:
            status = incoming.get("status") or getattr(self.websocket, "status", 0)
            setattr(self.websocket, "status", status)

        if roots.scope_slug == "sn":
            return await exam_control_socket_handler(roots.resource_type, incoming)

        socket_ses = get_request_session(self.websocket, self.request)
        if roots.scope_slug == "connect":
            return await self.connect_exam(socket_ses)

        roll_no = self.websocket.state.member.get("roll_no")
        req_sess, stu_rec, exm = getattr(
            self.websocket, "exam_info", (None, None, None)
        )

        if not stu_rec:
            req_sess = await StudentRequestSession.connect(
                roll_no, socket_ses.connection_id
            )

            stu_rec = (
                await Student.get_by_exam(
                    req_sess.roll_no, req_sess.exam_id, RecordType.INVIGILATOR
                )
                if req_sess
                else await Student.get_by_exam_key(
                    socket_ses.hx_key, RecordType.STUDENT
                )
            )

            if not stu_rec or stu_rec.roll_no != roll_no:
                return format_close_response(remove_exam_message("/"))

            if req_sess:
                exm = await Exam.get(stu_rec.exam_id)
                exm_data = await get_exam_dick(exm)

                if is_expired_exam(exm_data["endTime"]):
                    return format_close_response(
                        exam_timeout_message(
                            TimeStamp.format_ts(exm_data["endTime"]), "/"
                        )
                    )

                async def on_disconnect():
                    if req_sess.joined_status != ExamRqStatus.STUDENT_COMPLETED_EXAM:
                        req_sess.joined_status = ExamRqStatus.STUDENT_LEFT_EXAM
                        req_sess.leave_timestamps.append(TimeStamp.now_timestamp())
                        if await StudentRequestSession.update(req_sess):
                            await push_exam_event_by_joined_status(req_sess)

                self.websocket.state.disconnect_callback["req_sess_update"] = on_disconnect

                req_sess.joined_status = ExamRqStatus.STUDENT_JOINED_EXAM
                req_sess.join_timestamps.append(TimeStamp.now_timestamp())

                await push_exam_event_by_joined_status(req_sess)
                await StudentRequestSession.update(req_sess)

            setattr(self.websocket, "exam_info", (req_sess, stu_rec, exm))

        # Handle Initialized state
        if socket_ses.status == SessionStatus.INITIALIZED:
            if not is_valid_session(roll_no, socket_ses, incoming):
                return format_close_response(get_invalid_activity_error())

            return (
                await self.get_exam_data(socket_ses, stu_rec, exm, incoming)
                if stu_rec and exm
                else await self.get_self_exam_data(socket_ses, stu_rec)
            )

        # Handle Connected state
        elif socket_ses.status == SessionStatus.CONNECTED and incoming:
            if req_sess:
                is_valid, session = await StudentRequestSession.connect(
                    roll_no, req_sess.connect_key, True
                )
                if is_valid is None:
                    return format_close_response(
                        {
                            "action": "fe40dt",
                            "title": session.get("title"),
                            "desc": [session.get("message")],
                        }
                    )

            if not is_valid_session(roll_no, socket_ses, incoming):
                return format_close_response(get_invalid_activity_error())

            keys = await self.update_exam_status(incoming, stu_rec, exm, req_sess)

            if stu_rec and hasattr(stu_rec, "exam_id") and hasattr(stu_rec, "roll_no"):
                await ExamEventManager.update_student_status(
                    stu_rec.exam_id, stu_rec.roll_no
                )

            if keys and incoming.get("submit"):
                content = (
                    testSubmitted.get("English", "Test submitted.")
                    if exm
                    else exam_submitted_message(f"/exam/result/do/{keys}")
                )
                return format_close_response(content)

            if exm:
                exm = await Exam.get(exm.id)
                setattr(self.websocket, "exam_info", (req_sess, stu_rec, exm))
                return {"__ac": {119: calculate_exam_stats(exm)}}

        return {}