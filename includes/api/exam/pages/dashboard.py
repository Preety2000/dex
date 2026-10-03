from sqlalchemy import select, func, desc

from includes.core.globals.entry import app_context
from includes.db.connection import active_exam_db
from includes.api.exam.index import get_exam_dick
from includes.db.dataclass import serialize
from includes.db.models.utils import TimeStamp
from includes.db.models.db_exam import (
    ExamDetails,
    ExamRecord,
    ExamRequestSession,
)


def get_countion_grouped_by_exam(db):

    # Student count grouped by exam
    student_count = (
        select(
            ExamRecord.exam_id.label("exam_id"),
            func.count(ExamRecord.id).label("joined"),
        )
        .group_by(ExamRecord.exam_id)
        .subquery()
    )

    # Request count grouped by exam
    request_count = (
        select(
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

        stmt = (
            select(ExamRecord)
            .join(
                ExamRequestSession,
                ExamRecord.roll_no == ExamRequestSession.roll_no,
            )
            .join(
                ExamDetails,
                ExamRecord.exam_id == ExamDetails.id,
            )
            .where(ExamDetails.teacher_id == member_id)
            .where(ExamRecord.is_submitted.is_(True))
            .order_by(ExamRecord.allmarks.desc())
            .limit(10)
        )

        result = db.execute(stmt)

        records = result.scalars().all()

        return [get_list_student(item) for item in records]

    @staticmethod
    async def get_exam_record(
        member_id: int = None,
    ):

        db = await active_exam_db()

        # -------------------------------------------------
        # Total Exam Count
        # -------------------------------------------------

        total_count_stmt = select(func.count(ExamDetails.id)).where(
            ExamDetails.teacher_id == member_id
        )

        total_count = db.execute(total_count_stmt).scalar_one()

        # -------------------------------------------------
        # Total Students Joined
        # -------------------------------------------------

        students_joined_stmt = (
            select(func.count(func.distinct(ExamRecord.roll_no)))
            .join(
                ExamDetails,
                ExamRecord.exam_id == ExamDetails.id,
            )
            .where(ExamDetails.teacher_id == member_id)
        )

        students_joined = db.execute(students_joined_stmt).scalar_one()

        # -------------------------------------------------
        # Total Student Requests
        # -------------------------------------------------

        student_requests_stmt = (
            select(func.count(func.distinct(ExamRequestSession.roll_no)))
            .join(
                ExamDetails,
                ExamRequestSession.exam_id == ExamDetails.id,
            )
            .where(ExamDetails.teacher_id == member_id)
        )

        student_requests = db.execute(student_requests_stmt).scalar_one()

        # -------------------------------------------------
        # Grouped Student / Request Count
        # -------------------------------------------------

        (
            student_count,
            request_count,
        ) = get_countion_grouped_by_exam(db)

        # -------------------------------------------------
        # Exam List
        # -------------------------------------------------

        base_stmt = (
            select(
                ExamDetails,
                func.coalesce(
                    student_count.c.joined,
                    0,
                ).label("students_joined"),
                func.coalesce(
                    request_count.c.requests,
                    0,
                ).label("student_requests"),
            )
            .outerjoin(
                student_count,
                student_count.c.exam_id == ExamDetails.id,
            )
            .outerjoin(
                request_count,
                request_count.c.exam_id == ExamDetails.id,
            )
            .where(ExamDetails.teacher_id == member_id)
        )

        # -------------------------------------------------
        # Published Results Count
        # -------------------------------------------------

        published_stmt = select(func.count(ExamDetails.id)).where(
            ExamDetails.teacher_id == member_id,
            ExamDetails.publish_timestamp < TimeStamp.now_timestamp(),
        )

        published = db.execute(published_stmt).scalar_one()

        # -------------------------------------------------
        # Recent Exams
        # -------------------------------------------------

        exams_stmt = base_stmt.order_by(ExamDetails.timestamp.desc()).limit(10)

        exams_result = db.execute(exams_stmt)

        exams = exams_result.all()

        records = []

        for (
            record,
            student_recd,
            request_recd,
        ) in exams:

            exam_details = await get_exam_dick(record)

            records.append(
                {
                    "studentsJoined": student_recd,
                    "studentRequests": request_recd,
                    "exam_name": exam_details["exam_name"],
                    "testCode": exam_details["code"],
                    "testCreationTime": exam_details["timestampFormat"],
                    "testOpeningTime": exam_details["startTimeFormat"],
                    "timing": (f"{exam_details['totalTime']} Min"),
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
            "src": (
                "/media/u/"
                "cmFqa2FtYWxAZ21haWwuY29t/"
                "SU1HXzIwMjUwODA3XzAxMDg0Ny5qcGc"
                "?size=50x50"
            ),
            "height": 50,
            "width": 50,
            "title": "User Image",
        }

        records.update(
            {
                "__ac": 105,
                # -------------------------------------------------
                # Rank List
                # -------------------------------------------------
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
                # -------------------------------------------------
                # Top Student Test Participation
                # -------------------------------------------------
                "topStudentTestParticipation": [
                    {
                        "studentName": "Alice Johnson",
                        "testsJoined": 0,
                    },
                    {
                        "studentName": "David Lee",
                        "testsJoined": 0,
                    },
                    {
                        "studentName": "Emma Watson",
                        "testsJoined": 0,
                    },
                ],
                # -------------------------------------------------
                # Question Suggestions
                # -------------------------------------------------
                "questionSuggestionReport": [
                    {
                        "question": ("What is Newton's second law?"),
                        "suggestedBy": "Carlos Rivera",
                    },
                    {
                        "question": ("Explain the Treaty of Versailles."),
                        "suggestedBy": "Emma Watson",
                    },
                ],
                "totalTestResultsPublished": 0,
            }
        )

        return records
