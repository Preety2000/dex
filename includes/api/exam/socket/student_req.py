import os
from dataclasses import fields
from typing import Optional

from sqlalchemy import delete, func, select

from includes.utils.exm import get_exam_status_message
from includes.core.globals.entry import app_context
from includes.database.connection import active_exam_db
from includes.database.dataclass.dataclass import ExamRqStatus
from includes.database.models.db_exam import (
    _ExamRequestSession,
    ExamRequestSession,
)
from includes.api.exam.session.ev import ExamEventManager
from includes.database.models.utils import TimeStamp

user_id = []
student_request_session = {}
SRSCache = {}


class StudentRequestSession:

    @staticmethod
    def _cache(sr_ses):
        SRSCache[sr_ses.roll_no] = sr_ses
        return sr_ses

    @staticmethod
    def _cache_delete(sr_ses):
        SRSCache.pop(sr_ses.roll_no, None)
        return sr_ses

    @staticmethod
    async def get_with__cache_by_rollno(
        rollno: int,
        teacher_id: int,
        option: bool = None,
    ):
        record = SRSCache.get(rollno)

        if record:
            return record

        db = await active_exam_db()

        stmt = select(ExamRequestSession).where(
            ExamRequestSession.roll_no == int(rollno),
            ExamRequestSession.teacher_id == teacher_id,
        )

        if option is True:
            return db.execute(stmt).scalars()

        record = db.execute(stmt).scalars().first()

        if record:
            return StudentRequestSession._cache(record.to_dataclass())

        return None

    @staticmethod
    async def is_valid(session):
        return (
            (
                None,
                await get_exam_status_message(session.joined_status),
            )
            if session.joined_status
            in [
                ExamRqStatus.BLOCK_IN_EXAM,
                ExamRqStatus.REQUEST_REJECTED,
                ExamRqStatus.STUDENT_REMOVED_FROM_EXAM,
            ]
            else (
                True,
                session,
            )
        )

    @staticmethod
    async def create_request(
        exam_id,
        teacher_id,
        roll_no,
        student_name,
        profile_image,
        req_appr_mode,
    ):

        now = TimeStamp.now_iso()

        stmt = select(ExamRequestSession).where(
            ExamRequestSession.roll_no == int(roll_no),
            ExamRequestSession.exam_id == int(exam_id),
        )

        db = await active_exam_db()

        row = db.execute(stmt).scalars().first()

        if not row:
            row = ExamRequestSession(
                exam_id=exam_id,
                teacher_id=teacher_id,
                roll_no=roll_no,
                student_name=student_name,
                profile_image=profile_image,
                is_joined=True,
                is_re_requested=False,
                total_exam_joins=0,
                total_request=1,
                request_timestamps=[now],
                connect_key=os.urandom(5).hex(),
            )

            db.add(row)

        else:
            row.total_request += 1
            row.connect_key = os.urandom(5).hex()
            row.request_timestamps = [
                *(row.request_timestamps or []),
                now,
            ]

        if req_appr_mode == 0:
            row.joined_status = ExamRqStatus.STUDENT_PENDING_EXAM

        db.commit()
        db.refresh(row)

        if row.joined_status == ExamRqStatus.STUDENT_REQUEST_SEND:
            (
                completed_count,
                joined_count,
                request_count,
            ) = await StudentRequestSession.get_with_is_joined(exam_id)

            await ExamEventManager.push_exam_event(
                exam_id,
                [
                    5060,
                    {
                        "students": {
                            row.id: [
                                row.student_name,
                                row.roll_no,
                                row.profile_image,
                            ]
                        },
                        "STUDENT_REQUEST_SEND": [
                            [
                                row.id,
                                [
                                    row.total_request,
                                    row.request_timestamps[-1],
                                    None,
                                    row.joined_status,
                                ],
                            ]
                        ],
                        "STUDENT_REQUEST_SEND_COUNT": (request_count),
                        "STUDENT_JOINED_EXAM_COUNT": (joined_count),
                        "STUDENT_COMPLETED_EXAM_COUNT": (completed_count),
                    },
                ],
            )

        return row

    @staticmethod
    async def connect(
        roll_no: int,
        connect_key: str,
        check_status=None,
    ) -> Optional[ExamRequestSession]:

        await active_exam_db()

        record = SRSCache.get(roll_no)

        if record and record.connect_key == connect_key:
            return (
                await StudentRequestSession.is_valid(record) if check_status else record
            )

        stmt = select(ExamRequestSession).where(
            ExamRequestSession.roll_no == int(roll_no),
            ExamRequestSession.connect_key == connect_key,
        )
        db = await active_exam_db()
        record = db.execute(stmt).scalars().first()

        if not record:
            return None

        record = StudentRequestSession._cache(record.to_dataclass())

        return await StudentRequestSession.is_valid(record) if check_status else record

    @staticmethod
    async def _get(
        exam_id: int,
        roll_no: int,
    ) -> tuple[
        Optional[ExamRequestSession],
        list[ExamRequestSession],
    ]:

        base_stmt = select(ExamRequestSession).where(
            ExamRequestSession.exam_id == int(exam_id)
        )

        roll_stmt = base_stmt.where(ExamRequestSession.roll_no == int(roll_no))

        record = db.execute(roll_stmt).scalars().first()

        records = db.execute(base_stmt).scalars().all()

        return record, records

    @staticmethod
    async def getAll(
        *,
        limit: int = None,
        **filter,
    ) -> Optional[ExamRequestSession]:

        db = await active_exam_db()

        conditions = [
            getattr(ExamRequestSession, key) == value
            for key, value in filter.items()
            if value is not None
        ]

        stmt = select(ExamRequestSession).where(*conditions)

        if limit is not None:
            stmt = stmt.limit(limit)

        return db.execute(stmt).scalars().all()

    @staticmethod
    async def get(**filter) -> Optional[ExamRequestSession]:

        conditions = [
            getattr(ExamRequestSession, key) == value
            for key, value in filter.items()
            if value is not None
        ]

        stmt = select(ExamRequestSession).where(*conditions)
        db = await active_exam_db()
        record = db.execute(stmt).scalars().first()

        return StudentRequestSession._cache(record.to_dataclass()) if record else None

    @staticmethod
    async def update(
        callback,
        **filter,
    ) -> Optional[ExamRequestSession]:
        """Active exam database"""

        print("___student_update_requrst")

        if not (callable(callback) or isinstance(callback, _ExamRequestSession)):
            return None

        conditions = [
            getattr(ExamRequestSession, key) == value
            for key, value in filter.items()
            if value is not None
        ]

        db = await active_exam_db()
        if callable(callback):

            stmt = select(ExamRequestSession).where(*conditions)
            row = db.execute(stmt).scalars().first()

            if row:
                # Callback ko query object ki jagah
                # statement/result context dena zaroori ho
                # sakta hai. Existing callback compatibility
                # ke liye row ko second argument diya gaya hai.
                dt = await callback(
                    row,
                    stmt,
                )

                db.commit()
                db.refresh(row)

                return (
                    StudentRequestSession._cache(row.to_dataclass())
                    if isinstance(
                        dt,
                        ExamRequestSession,
                    )
                    else dt
                )

            return None

        if isinstance(callback, _ExamRequestSession):

            stmt = select(ExamRequestSession).where(
                ExamRequestSession.id == callback.id
            )

            row = db.execute(stmt).scalars().first()

            if not row:
                return None

            if row.joined_status in [
                ExamRqStatus.BLOCK_IN_EXAM,
                ExamRqStatus.REQUEST_REJECTED,
                ExamRqStatus.STUDENT_REMOVED_FROM_EXAM,
            ]:
                return None

            for field in fields(callback):
                setattr(
                    row,
                    field.name,
                    getattr(
                        callback,
                        field.name,
                    ),
                )

            db.commit()
            db.refresh(row)

            return StudentRequestSession._cache(row.to_dataclass())

        return None

    @staticmethod
    async def delete(
        **filter,
    ) -> Optional[ExamRequestSession]:

        conditions = [
            getattr(ExamRequestSession, key) == value
            for key, value in filter.items()
            if value is not None
        ]

        select_stmt = select(ExamRequestSession).where(*conditions)
        db = await active_exam_db()
        record = db.execute(select_stmt).scalars().first()

        if record:
            cached = SRSCache.get(record.roll_no)

            if cached and cached.id == record.id:
                print("--------------------------delete", cached)

                SRSCache.pop(cached.roll_no, None)

        delete_stmt = delete(ExamRequestSession).where(*conditions)

        db.execute(delete_stmt)
        db.commit()

        return record

    @staticmethod
    async def get_with_is_joined(
        exam_id: Optional[int],
        *,
        offset: int = 0,
        limit: int = 10,
        joined_record: bool = None,
    ):

        base_stmt = select(ExamRequestSession).where(
            ExamRequestSession.exam_id == exam_id
        )

        joined_statuses = [
            ExamRqStatus.STUDENT_JOINED_EXAM,
            ExamRqStatus.STUDENT_PENDING_EXAM,
            ExamRqStatus.STUDENT_LEFT_EXAM,
        ]

        request_statuses = [
            ExamRqStatus.STUDENT_REQUEST_SEND,
            ExamRqStatus.REQUEST_REJECTED,
        ]

        completed_statuses = [ExamRqStatus.STUDENT_COMPLETED_EXAM]

        joined_stmt = base_stmt.where(
            ExamRequestSession.joined_status.in_(joined_statuses)
        )

        request_stmt = base_stmt.where(
            ExamRequestSession.joined_status.in_(request_statuses)
        )

        completed_stmt = base_stmt.where(
            ExamRequestSession.joined_status.in_(completed_statuses)
        )

        # Counts
        db = await active_exam_db()
        joined_count = db.execute(
            select(func.count())
            .select_from(ExamRequestSession)
            .where(
                ExamRequestSession.exam_id == exam_id,
                ExamRequestSession.joined_status.in_(joined_statuses),
            )
        ).scalar_one()

        request_count = db.execute(
            select(func.count())
            .select_from(ExamRequestSession)
            .where(
                ExamRequestSession.exam_id == exam_id,
                ExamRequestSession.joined_status.in_(request_statuses),
            )
        ).scalar_one()

        completed_count = db.execute(
            select(func.count())
            .select_from(ExamRequestSession)
            .where(
                ExamRequestSession.exam_id == exam_id,
                ExamRequestSession.joined_status.in_(completed_statuses),
            )
        ).scalar_one()

        if joined_record:

            students = {}
            result = []

            joined_records = (
                db.execute(joined_stmt.offset(offset).limit(limit)).scalars().all()
            )

            for record in joined_records:
                students[record.id] = "student_info"

                result.append(
                    [
                        record.id,
                        record.join_timestamps,
                        record.joined_status,
                        record.total_exam_joins,
                        record.is_re_requested,
                        record.is_joined,
                    ]
                )

            return (
                students,
                result,
                joined_count,
                request_count,
            )

        return (
            completed_count,
            joined_count,
            request_count,
        )
