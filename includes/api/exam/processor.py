from includes.api.exam.student import RecordType, Student
from includes.api.exam.session.es import ES
from includes.api.exam.teacher import Teachers
from includes.core.metadata import MetaData
from includes.utils.exm import (
    block_exam_message,
    completed_exam_message,
    exam_not_started_message,
    exam_submitted_message,
    get_exam_status_message,
    get_request_rejected_message,
    is_expired_exam,
    time_until,
)
from includes.api.exam.index import Exam, get_exam_dick
from includes.api.exam.manager.practice import SELF_EXAM_MANAGER
from includes.api.exam.session.ev import ExamEventManager
from includes.api.exam.socket.index import init_exam_session
from includes.api.exam.socket.student_req import StudentRequestSession
from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.db.dataclass import ExamRqStatus
from includes.db.models.db_exam import _ExamDetails, StudentTeacherAssociation
from includes.function import get_unique_id
from includes.utils.utils import json_response


async def check_access(
    exam_query: _ExamDetails, st_roll_no: int
) -> tuple[bool, bool | None]:

    if exam_query.join_mode == 2:
        return True, None

    db = await app_context.db.configure_exam()
    link = (
        db.query(StudentTeacherAssociation)
        .filter_by(st_roll_no=st_roll_no, teacher_id=exam_query.teacher_id)
        .first()
    )

    if not link:
        return False, None

    if exam_query.join_mode == 1:
        return True, None

    return (
        (True, True)
        if exam_query.join_mode == 0 and link.link_status == 1
        else (False, None)
    )


class ExamtProcessor:
    def __init__(self, isuser=None):
        self.isuser = isuser

    async def handle_exam_request(self, path: str, params: dict):

        join = params.get("join")
        has_keys = params.get("hx")
        response = {}
        if path != "/exam":
            return response

        if not join and not has_keys:
            return response

        member = await app_context.setting.member()
        
        if member is None:
            MetaData.redirect_url = "/exam"
            return response
            
        stu_rec = StudentRequestSession.get(
            roll_no=member.get("roll_no"), has_key=has_keys
        )

        print("has_keys", has_keys)

        # Case 1: Session injection without time restriction
        if has_keys and stu_rec is None:
            await self.inject_exam_session(response, has_keys)
            return self.return_response(response)

        if has_keys and stu_rec.joined_status in [
            ExamRqStatus.BLOCK_IN_EXAM,
            ExamRqStatus.REQUEST_REJECTED,
            ExamRqStatus.STUDENT_REMOVED_FROM_EXAM,
        ]:
            print("edite this session for message")
            await self.inject_exam_session(response, has_keys)
            return self.return_response(response)

        # Case 2: Joining an exam
        if join and (join := int(join)):
            response.update(await self.process_join_exam(join, member))
            if response.get("request_status") is False:
                response["content"] = get_request_rejected_message(response)

            print(response, "rrrrr")
            return self.return_response(response, 114)

        # Case 3: Regular exam processing
        return await self.process_exam(stu_rec, response)

    async def inject_exam_session(self, response, has_keys):
        self_exam_manager = SELF_EXAM_MANAGER()
        await self_exam_manager.session_inject(response, has_keys)

        response["stu_img"] = self.isuser.get("img")
        response["reg_no"] = self.isuser.get("reg_no")
        response["stu_name"] = self.isuser.get("name")
        response["roll_no"] = self.isuser.get("roll_no")

    async def process_join_exam(self, exam_id: int, student):
        response = {"status": None}

        # Fetch exam details
        exam_query = await Exam.get(exam_id)

        if not exam_query:
            response["message"] = "No matching exam found. Please enter a valid code."
            return response

        if not exam_query.start_timestamp:
            response["message"] = (
                "The exam is not available yet. Please wait for the exam to begin. If you need help, please contact your instructor."
            )
            return response

        # Get teacher and student details
        teachers = await Teachers.get(exam_query.teacher_id)
        roll_no = student.get("roll_no")

        # Check if student already submitted the exam
        student_exam_record = await Student.get_by_exam(roll_no, exam_id, 1)
        if student_exam_record and student_exam_record.is_submitted:
            response.update(
                completed_exam_message(
                    student_exam_record.timestamp,
                    f"/exam/result/{student_exam_record.key}",
                )
            )
            return response

        # Check if exam is expired
        exam_dick = await get_exam_dick(exam_query)

        if is_expired_exam(exam_dick["endTime"]):
            response["message"] = "This exam session has expired and is now closed."
            return response

        # Handle join mode and request logic
        join_mode = exam_dick["join_mode"]
        join_status, request_status = await check_access(exam_query, roll_no)

        response["status"] = "close"
        if join_status:
            response.update(
                {
                    "code": exam_dick["code"],
                    "teacherName": teachers.name,
                }
            )

            print("open_request", exam_query.open_request)

            # ["active_only", "24_hours", "lifetime"]
            if (
                exam_query.open_request == 0
                and await ExamEventManager.get_availability(exam_query.id, 2000)
            ):
                response["title"] = "No Exam Available"
                response["message"] = (
                    "No online exam is currently available. Please check again later."
                )
                return response

            if (
                exam_query.open_request == 1
                and await ExamEventManager.get_availability(exam_query.id)
            ):
                response["title"] = "No Exam Available"
                response["message"] = (
                    "No online exam is currently available. Please check again later."
                )
                return response

            connect_session = await StudentRequestSession.create_request(
                exam_query.id,
                exam_query.teacher_id,
                student.get("roll_no"),
                student.get("name"),
                student.get("img"),
                exam_query.req_appr_mode,
            )

            if connect_session.joined_status in [
                ExamRqStatus.REQUEST_REJECTED,
                ExamRqStatus.BLOCK_IN_EXAM,
                ExamRqStatus.STUDENT_REMOVED_FROM_EXAM,
            ]:
                message = await get_exam_status_message(connect_session.joined_status)
                response.update(message)
                return response

            if connect_session.joined_status == ExamRqStatus.STUDENT_COMPLETED_EXAM:
                return {
                    "status": "close",
                    "statusCode": connect_session.joined_status,
                    "content": exam_submitted_message(
                        f"/exam/result/{student_exam_record.key}"
                    ),
                }

            if request_status is True or (
                connect_session.joined_status
                in [
                    ExamRqStatus.STUDENT_LEFT_EXAM,
                    ExamRqStatus.STUDENT_JOINED_EXAM,
                    ExamRqStatus.STUDENT_PENDING_EXAM,
                ]
            ):

                record = await init_exam_session(connect_session, exam_query)
                origin = app_context.request.headers.get("origin")
                return {
                    "status": "open",
                    "infoMessage": "Request accepted",
                    "statusCode": connect_session.joined_status,
                    "joinLink": f"{origin}/exam?hx={record.has_key}",
                }

            response.update(
                {
                    "status": "open",
                    "connect_key": connect_session.connect_key,
                    "statusCode": connect_session.joined_status,
                    "teacherImg": teachers.img,
                    "exam_name": exam_dick["exam_name"],
                    "startTimeFormat": exam_dick["startTimeFormat"],
                }
            )

        elif join_mode == "approvalRequired":
            response["message"] = "Only approved students can send a join request."

        elif join_mode == "directAccess":
            response["message"] = (
                "Only approved students can join directly. Join requests are not allowed."
            )

        response["join_mode"] = join_mode
        return response

    async def process_exam(self, stu_rec, response):
        print("process_exam")
        try:
            try:
                exam_id_decoded = _Security.short_decode(stu_rec.exam_id)
            except Exception as e:
                exam_id_decoded = stu_rec.exam_id

            studebt_exam_record = await Student.get_by_exam_key(
                stu_rec.srec_kry, RecordType.INVIGILATOR
            )

            if not studebt_exam_record or studebt_exam_record.exam_id != int(
                exam_id_decoded
            ):
                print("studebt_exam_record not fond")
                return self.return_response(response, 100)

            if studebt_exam_record.is_submitted == False:  # Exam not submitted
                session_key = get_unique_id()
                if stu_rec.started_at and ES.add(stu_rec.roll_no, session_key):
                    target_time, total_seconds = time_until(stu_rec.started_at)
                    days_remaining = total_seconds // (60 * 60 * 24)

                    if days_remaining <= 0:
                        response["id"] = stu_rec.has_key
                        response["session_key"] = session_key
                        response["connect_key"] = stu_rec.connect_key
                        return self.return_response(response, 117)

                    response["content"] = exam_not_started_message(target_time)
                    return self.return_response(response, 116)

                print("_________error 2")

            elif studebt_exam_record.is_submitted == True:
                href = f"/exam/result/{stu_rec.srec_kry}"
                response["content"] = exam_submitted_message(href)
                return self.return_response(response, 116)

        except Exception as e:
            print(f"Error processing exam: {e}")
            return self.return_response(response, 100)

    def return_response(self, response, code=None):
        if code is not None:
            response["__ac"] = code
        return json_response(response)
