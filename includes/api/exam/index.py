import math

from sqlalchemy import and_, desc
from includes.api.exam.socket.student_req import StudentRequestSession
from includes.api.exam.student import Student
from includes.db.connection import active_exam_db
from includes.db.models.utils import TimeStamp
from includes.core.globals.entry import app_context
from includes.core.pagination import Pagination
from includes.core.request_filter import RequestFilter
from includes.db.dataclass import serialize
from includes.db.models.db_exam import (
    _ExamDetails,
    ExamDetails,
    ExamRecord,
    ExamRequestSession,
)
from includes.core.security import _Security
from includes.api.exam.teacher import Teachers
from includes.utils.exm import (
    calculate_exam_stats,
    convert_int_values,
)
from includes.api.exam.metadata import (
    get_class_name,
    s_meta_value,
    exam_setting_setter,
    get_selected_classes,
    get_mode_option_title,
)
from includes.utils.meb import extract_id_from_roll

ExamTamp = {}


async def get_exam_dick(query, option=False):
    language = await app_context.setting.get("language", "English")

    def get_value(options, index, default):
        return (
            options[index]
            if isinstance(index, int) and 0 <= index < len(options)
            else options[default]
        )

    join_mode = get_value(s_meta_value.get("join_mode", []), query.join_mode, 2)
    open_request = get_value(
        s_meta_value.get("open_request", []), query.open_request, 0
    )
    req_appr_mode = get_value(
        s_meta_value.get("req_appr_mode", []), query.req_appr_mode, 2
    )
    result_visibility = get_value(
        s_meta_value.get("result_visibility", []), query.result_visibility, 0
    )

    data = calculate_exam_stats(query)
    details = convert_int_values(query.details)
    join_mode_title = get_mode_option_title("join_mode", join_mode, language)
    open_request_title = get_mode_option_title("open_request", open_request, language)
    # req_appr_mode_title = get_mode_option_title("req_appr_mode", req_appr_mode, language)
    data.update(
        {
            "id": _Security.short_encode(str(query.id)),
            "code": query.id,
            "exam_category": get_class_name(query.exam_category or "any"),
            "join_mode": join_mode,
            "open_request": open_request,
            "req_appr_mode": req_appr_mode,
            "joinModeTitle": join_mode_title,
            "openRequestTitle": open_request_title,
            "result_visibility": result_visibility,
            "notification": query.notification,
            "details": details,
            "exam_name": query.exam_name,
            "start_timestamp": query.start_timestamp,
            "timestamp": query.timestamp,
            "publishTime": query.publish_timestamp,
            "isPublish": (query.publish_timestamp or (TimeStamp.now_timestamp() + 5000))
            < TimeStamp.now_timestamp(),
            "startTimeFormat": TimeStamp.format_ts(
                query.start_timestamp, "%d %B, %Y at %I:%M %p"
            ),
            "timestampFormat": TimeStamp.format_ts(
                query.timestamp, "%d %B, %Y at %I:%M %p"
            ),
            "publishTimeFormat": TimeStamp.format_ts(
                query.publish_timestamp, "%d %B, %Y at %I:%M %p"
            ),
        }
    )
    if option == True:
        data.update({"questions": query.questions})
    return data


class Exam:

    @staticmethod
    async def with_catch(data: ExamDetails):
        ExamTamp[data.id] = data.to_dataclass()
        return ExamTamp[data.id]

    @staticmethod
    async def get(exam_id: int) -> _ExamDetails:
        exam_id = int(exam_id)
        if exam_id in ExamTamp:
            return ExamTamp[exam_id]

        query = (
            app_context.db.query(ExamDetails).filter(ExamDetails.id == exam_id).first()
        )
        return await Exam.with_catch(query) if query else None

    @staticmethod
    async def _update(data: _ExamDetails) -> _ExamDetails:
        db = await active_exam_db()
        _data = serialize(data)
        del _data["id"]
        del _data["keys"]
        del _data["details"]
        del _data["publish"]
        del _data["exam_name"]
        del _data["questions"]
        del _data["timestamp"]
        del _data["teacher_id"]
        del _data["teacher_record"]

        exam = db.query(ExamDetails).filter(ExamDetails.id == data.id).first()
        for key, value in _data.items():
            if hasattr(exam, key):
                setattr(exam, key, value)

        db.commit()
        db.refresh(exam)

        return await Exam.with_catch(exam)

    @staticmethod
    async def update(exam_id: int, data: dict) -> _ExamDetails:
        db = await active_exam_db()
        exam = db.query(ExamDetails).filter_by(id=exam_id).first()
        if not exam:
            return None

        await exam_setting_setter(exam, data)
        for key, value in data.items():
            setattr(exam, key, value)

        db.commit()
        db.refresh(exam)
        return await Exam.with_catch(exam)

    @staticmethod
    async def delete(exam_id: int, timestamp: int = None):
        if timestamp is None:
            return {"status": False, "message": "Exam details not found."}

        db = await active_exam_db()
        query = (
            db.query(ExamDetails)
            .filter(
                ExamDetails.id == int(exam_id),
                ExamDetails.timestamp == timestamp,
            )
            .first()
        )

        if not query:
            return {"status": False, "message": "Exam details not found."}

        for record in db.query(ExamRecord).filter(ExamRecord.exam_id == query.id).all():
            Student._cache_delete(record)
            db.delete(record)

        for record in (
            db.query(ExamRequestSession)
            .filter(ExamRequestSession.exam_id == query.id)
            .all()
        ):
            StudentRequestSession._cache_delete(record)
            db.delete(record)

        db.delete(query)
        db.commit()

        return {
            "status": True,
            "message": "Exam details and all related records deleted successfully.",
        }

    @staticmethod
    async def get_lists(id: int, limit: int = 10, page: int = 0):
        query = await RequestFilter.apply_request_filters(
            model=ExamDetails,
            request_type="referer",
            query=app_context.db.query(ExamDetails).filter(
                ExamDetails.teacher_id == id
            ),
            columns={
                "exam_category": "category",
                "exam_name": "name",
                "timestamp": "date",
                "id": "exam_id",
            },
            search_columns=["category", "name", "exam_id"],
        )

        total = query.count()

        pagination = Pagination("referer")
        await pagination.load(limit=limit)
        offset = pagination.get_offset()

        records = (
            query.order_by(ExamDetails.timestamp.desc())
            .offset(offset)
            .limit(pagination.limit)
            .all()
        )

        async def enrich_student(record):
            return await get_exam_dick(record)

        processed_data, pagination_data, total = await pagination.paginate(
            total=total,
            data=records,
            transform=enrich_student,
        )
        return processed_data, pagination_data, total

    @staticmethod
    async def get_with_details(exam_id: int):
        """Fetch detailed information about an exam by its ID."""

        exam_query = await Exam.get(exam_id)

        if not exam_query:
            return {}, exam_query

        # Fetch teacher details
        teacher = await Teachers.get(exam_query.teacher_id)

        if not exam_query:
            return {}, exam_query

        student_roll_numbers = []

        def add_roll_number(raw_roll):
            """
            Extracts and encodes a student's roll number.
            Also appends it to the global roll number list.
            """
            roll_no = extract_id_from_roll(raw_roll)
            student_roll_numbers.append(roll_no)
            encoded = _Security.number_encode(roll_no)
            return encoded

        # Convert the exam record into JSON
        response = await get_exam_dick(exam_query, True)

        # Get teacher’s competitive classes
        competitive_classes = get_selected_classes(teacher.exam_category)
        competitive_classes.append(["any", "Any"])
        response["class"] = competitive_classes
        response["useFaxId"] = exam_query.teacher_id

        # Fetch all student exam records for this exam
        student_exam_query = app_context.db.query(ExamRecord).filter(
            ExamRecord.exam_id == exam_id
        )
        # return response
        # Students who joined but haven’t completed
        response["studentJoined"] = [
            [
                add_roll_number(item.roll_no),
                item.timestamp,
            ]
            for item in student_exam_query.filter(
                ExamRecord.is_submitted == False
            ).all()
        ]
        # Students who completed the exam
        completed_query = student_exam_query.filter(ExamRecord.is_submitted == True)
        response["STUDENT_COMPLETED_EXAM_COUNT"] = completed_query.count()
        response["studentCompliteExam"] = [
            [
                add_roll_number(item.roll_no),
                item.is_submitted,
                item.allmarks,
                item.timestamp,
                item.submitted_on,
            ]
            for item in completed_query.order_by(desc(ExamRecord.submitted_on))
            .limit(10)
            .all()
        ]
        response["students"] = student_roll_numbers
        return response, exam_query
