from dataclasses import asdict
from includes.database.connection import active_exam_db
from includes.core.pagination import Pagination
from includes.core.request_filter import RequestFilter
from includes.database.models.db_exam import (
    _StudentTeacherAssociation,
    _TeacherProfile,
    ExamRequestSession,
    StudentTeacherAssociation,
)
from includes.schemas.cache.member import MemberCache


async def with_details(
    record: StudentTeacherAssociation,
    teacher: _TeacherProfile,
):
    db = await active_exam_db()
    student = await MemberCache.getrollnumber(record.st_roll_no) or {}

    attempt = (
        db.query(ExamRequestSession)
        .filter(
            ExamRequestSession.roll_no == record.st_roll_no,
            ExamRequestSession.teacher_id == teacher.id,
        )
        .count()
    )

    return {
        "rollno": record.st_roll_no,
        "timestamp": record.timestamp,
        "status": record.link_status,
        "exam_category": record.exam_category,
        "name": student.get("name"),
        "img": student.get("img"),
        "reg_no": student.get("reg_no"),
        "student": student,
        "attempt": attempt,
    }


STAMP = {}


class StLinks:

    @staticmethod
    async def _set_cache(data: _StudentTeacherAssociation):
        STAMP[(data.st_roll_no, data.teacher_id)] = data.to_dataclass()
        return STAMP[(data.st_roll_no, data.teacher_id)]

    @staticmethod
    async def _delete_cache(data: _StudentTeacherAssociation):
        STAMP.pop((data.st_roll_no, data.teacher_id), None)

    @staticmethod
    def _query(db, data: _StudentTeacherAssociation):
        return db.query(StudentTeacherAssociation).filter(
            StudentTeacherAssociation.st_roll_no == data.st_roll_no,
            StudentTeacherAssociation.teacher_id == data.teacher_id,
        )

    @staticmethod
    async def get(data: _StudentTeacherAssociation):
        key = (data.st_roll_no, data.teacher_id)
        if key in STAMP:
            return STAMP[key]

        db = await active_exam_db()
        query = StLinks._query(db, data).first()

        if not query:
            return None

        cached_data = await StLinks._set_cache(query)
        return cached_data

    @staticmethod
    async def create(data: _StudentTeacherAssociation):
        db = await active_exam_db()

        # Already exists
        if StLinks._query(db, data).first():
            return {
                "status": False,
                "message": "Student association already exists.",
            }

        query = StudentTeacherAssociation(
            teacher_id=data.teacher_id,
            st_roll_no=data.st_roll_no,
            exam_category=data.exam_category,
        )

        db.add(query)
        db.commit()
        db.refresh(query)

        cached_data = await StLinks._set_cache(query)
        return cached_data

    @staticmethod
    async def update(data: _StudentTeacherAssociation):
        db = await active_exam_db()

        query = StLinks._query(db, data).first()
        if not query:
            return {
                "status": False,
                "message": "Student association not found.",
            }

        if len(data.exam_category) > 0:
            query.exam_category = data.exam_category

        if data.link_status is not None:
            query.link_status = data.link_status

        db.commit()
        db.refresh(query)
        cached_data = await StLinks._set_cache(query)
        return cached_data

    @staticmethod
    async def delete(data: _StudentTeacherAssociation):
        db = await active_exam_db()
        query = StLinks._query(db, data).first()
        if query is None:
            return {
                "status": False,
                "message": "Student association not found.",
            }

        # Remove from cache
        await StLinks._delete_cache(query)
        db.delete(query)
        db.commit()

        return {
            "status": True,
            "message": "Student association deleted successfully.",
        }


class StLinksHendlar:

    @staticmethod
    async def add_student(
        *,
        exam_category: list | None = None,
        strollno: int | None = None,
        teacher=None,
    ):
        # Validate teacher session
        if not isinstance(teacher, _TeacherProfile):
            return {
                "status": False,
                "message": "Invalid teacher session.",
                "error_type": "invalid_session",
            }

        # Validate roll number
        if strollno is None:
            return {
                "status": False,
                "message": "Student roll number is required.",
                "error_type": "roll_number_required",
            }

        # Find student
        student = await MemberCache.getrollnumber(strollno)

        if not student:
            return {
                "status": False,
                "message": "No student found with the provided roll number.",
                "error_type": "student_not_found",
            }

        exam_category = exam_category or []
        query = _StudentTeacherAssociation(
            st_roll_no=strollno,
            exam_category=exam_category,
            teacher_id=teacher.id,
        )

        query = await StLinks.create(query)

        if not isinstance(query, _StudentTeacherAssociation):
            return query

        return {
            "status": True,
            "message": "Student added successfully.",
            "data": await with_details(query, teacher),
        }

    @staticmethod
    async def block_student(
        *,
        exam_category: list | None = None,
        strollno: int | None = None,
        teacher=None,
    ):
        return await StLinks.update(
            _StudentTeacherAssociation(
                st_roll_no=strollno, teacher_id=teacher.id, link_status=2
            )
        )

    @staticmethod
    async def update_student(
        *,
        exam_category: list | None = None,
        strollno: int | None = None,
        teacher=None,
    ):
        return await StLinks.update(
            _StudentTeacherAssociation(
                st_roll_no=strollno, teacher_id=teacher.id, exam_category=exam_category
            )
        )

    @staticmethod
    async def unblock_student(
        *,
        exam_category: list | None = None,
        strollno: int | None = None,
        teacher=None,
    ):
        return await StLinks.update(
            _StudentTeacherAssociation(
                st_roll_no=strollno, teacher_id=teacher.id, link_status=1
            )
        )

    @staticmethod
    async def delete_student(
        *,
        exam_category: list | None = None,
        strollno: int | None = None,
        teacher=None,
    ):
        return await StLinks.delete(
            _StudentTeacherAssociation(st_roll_no=strollno, teacher_id=teacher.id)
        )

    @staticmethod
    async def get_list(teacher: _TeacherProfile, limit: int = 10):
        db = await active_exam_db()

        query = await RequestFilter.apply_request_filters(
            model=StudentTeacherAssociation,
            request_type="referer",
            query=db.query(StudentTeacherAssociation).filter(
                StudentTeacherAssociation.teacher_id == teacher.id,
            ),
            columns={
                "exam_category": "cls",
                "st_roll_no": "rollno",
            },
            search_columns=["rollno", "cls"],
        )

        total = query.count()

        pagination = Pagination("referer")
        await pagination.load(limit=limit)
        offset = pagination.get_offset()

        records = query.offset(offset).limit(pagination.limit).all()

        async def enrich_student(record):
            return await with_details(
                await StLinks._set_cache(record),
                teacher,
            )

        processed_data, pagination_data, total = await pagination.paginate(
            total=total,
            data=records,
            transform=enrich_student,
        )
        return processed_data, pagination_data, total
