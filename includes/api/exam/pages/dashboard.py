from sqlalchemy import func
from sqlalchemy import desc

from includes.core.globals.entry import app_context
from includes.db.connection import active_exam_db
from includes.api.exam.index import get_exam_dick
from includes.db.dataclass import serialize
from includes.db.models.utils import TimeStamp
from includes.db.models.db_exam import ExamDetails
from includes.db.models.db_exam import ExamRecord
from includes.db.models.db_exam import ExamRequestSession


def get_countion_grouped_by_exam(db):

    # Student count grouped by exam
    student_count = (
        db.query(
            ExamRecord.exam_id.label("exam_id"),
            func.count(ExamRecord.id).label("joined"),
        )
        .group_by(ExamRecord.exam_id)
        .subquery()
    )

    # Request count grouped by exam
    request_count = (
        db.query(
            ExamRequestSession.exam_id.label("exam_id"),
            func.count(ExamRequestSession.id).label("requests"),
        )
        .group_by(ExamRequestSession.exam_id)
        .subquery()
    )

    return student_count, request_count


def get_list_student(data: ExamRecord):
    data = serialize(data)
    rws = {
        "image": data,
        "studentName": None,
        "rank": None,
        "score": None,
    }
    return rws


class ExamDashboard:

    @staticmethod
    async def get_rank_student(member_id: int):
        db = await active_exam_db()
        result = (
            db.query(ExamRecord)
            .join(ExamRequestSession, ExamRecord.roll_no == ExamRequestSession.roll_no)
            .join(ExamDetails, ExamRecord.exam_id == ExamDetails.id)
            .filter(ExamDetails.teacher_id == member_id)
            .filter(ExamRecord.is_submitted.is_(True))
            .order_by(ExamRecord.allmarks.desc())
            .limit(10)
            .all()
        )

        return [get_list_student(item) for item in result]

    @staticmethod
    async def get_exam_record(member_id: int = None):

        db = await active_exam_db()

        total_count = (
            db.query(func.count(ExamDetails.id))
            .filter(ExamDetails.teacher_id == member_id)
            .scalar()
        )

        students_joined = (
            db.query(func.count(func.distinct(ExamRecord.roll_no)))
            .join(ExamDetails, ExamRecord.exam_id == ExamDetails.id)
            .filter(ExamDetails.teacher_id == member_id)
            .scalar()
        )

        student_requests = (
            db.query(func.count(func.distinct(ExamRequestSession.roll_no)))
            .join(ExamDetails, ExamRequestSession.exam_id == ExamDetails.id)
            .filter(ExamDetails.teacher_id == member_id)
            .scalar()
        )

        student_count, request_count = get_countion_grouped_by_exam(db)

        bese_record = (
            db.query(
                ExamDetails,
                func.coalesce(student_count.c.joined, 0).label("students_joined"),
                func.coalesce(request_count.c.requests, 0).label("student_requests"),
            )
            .outerjoin(student_count, student_count.c.exam_id == ExamDetails.id)
            .outerjoin(request_count, request_count.c.exam_id == ExamDetails.id)
            .filter(ExamDetails.teacher_id == member_id)
        )
        published = (
            db.query(func.count(ExamDetails.id))
            .filter(
                ExamDetails.teacher_id == member_id,
                ExamDetails.publish_timestamp < TimeStamp.now_timestamp(),
            )
            .scalar()
        )

        records = []
        exams = bese_record.order_by(desc(ExamDetails.timestamp)).limit(10).all()
        for record, student_recd, request_recd in exams:
            exam_details = await get_exam_dick(record)
            records.append(
                {
                    "studentsJoined": student_recd,
                    "studentRequests": request_recd,
                    "exam_name": exam_details["exam_name"],
                    "testCode": exam_details["code"],
                    "testCreationTime": exam_details["timestampFormat"],
                    "testOpeningTime": exam_details["startTimeFormat"],
                    "timing": f"{exam_details['totalTime']} Min",
                }
            )

        return {
            "recentExam": records,
            "totalExamCount": total_count,
            "totalResultsPublished": published,
            "studentsJoined": students_joined,
            "studentRequests": student_requests,
        }

    @staticmethod
    async def get_dashboard_data():
        member = await app_context.setting.member()
        records = await ExamDashboard.get_exam_record(member["id"])
        rank_student = await ExamDashboard.get_rank_student(member["id"])

        img = {
            "src": "/media/u/cmFqa2FtYWxAZ21haWwuY29t/SU1HXzIwMjUwODA3XzAxMDg0Ny5qcGc?size=50x50",
            "height": 50,
            "width": 50,
            "title": "User Image",
        }

        records.update(
            {
                "__ac": 105,
                "dataRankList": [
                    {
                        "image": img,
                        "studentName": "Alice Johnson",
                        "userName": "@member",
                        "rank": 1,
                        "score": 98,
                    },
                    {
                        "image": img,
                        "studentName": "Bob Smith",
                        "userName": "@member",
                        "rank": 2,
                        "score": 95,
                    },
                    {
                        "image": img,
                        "studentName": "Carlos Rivera",
                        "userName": "@member",
                        "rank": 3,
                        "score": 92,
                    },
                ],
                "topStudentTestParticipation": [
                    {"studentName": "Alice Johnson", "testsJoined": 0},
                    {"studentName": "David Lee", "testsJoined": 0},
                    {"studentName": "Emma Watson", "testsJoined": 0},
                ],
                "questionSuggestionReport": [
                    {
                        "question": "What is Newton's second law?",
                        "suggestedBy": "Carlos Rivera",
                    },
                    {
                        "question": "Explain the Treaty of Versailles.",
                        "suggestedBy": "Emma Watson",
                    },
                ],
                "totalTestResultsPublished": 0,
            }
        )

        return records
