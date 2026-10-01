import os
import uuid
from typing import Optional
from dataclasses import fields

from includes.utils.exm import get_exam_status_message
from includes.core.globals.entry import app_context
from includes.db.connection import active_exam_db
from includes.db.dataclass import ExamRqStatus
from includes.db.models.db_exam import _ExamRequestSession, ExamRequestSession
from includes.api.exam.session.ev import ExamEventManager
from includes.db.models.utils import TimeStamp

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
        rollno: int, teacher_id: int, option: bool = None
    ):
        record = SRSCache.get(rollno)
        if record:
            return record

        db = await active_exam_db()
        record = db.query(ExamRequestSession).filter_by(
            roll_no=int(rollno), teacher_id=teacher_id
        )
        if option is True:
            return record

        record = record.first()
        if record:
            return StudentRequestSession._cache(record.to_dataclass())

        return None

    @staticmethod
    async def is_valid(session):
        return (
            (None, await get_exam_status_message(session.joined_status))
            if session.joined_status
            in [
                ExamRqStatus.BLOCK_IN_EXAM,
                ExamRqStatus.REQUEST_REJECTED,
                ExamRqStatus.STUDENT_REMOVED_FROM_EXAM,
            ]
            else (True, session)
        )

    @staticmethod
    async def create_request(
        exam_id, teacher_id, roll_no, student_name, profile_image, req_appr_mode
    ):

        now = TimeStamp.now_iso()
        row = (
            app_context.db.query(ExamRequestSession)
            .filter_by(roll_no=int(roll_no), exam_id=int(exam_id))
            .first()
        )
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
            app_context.db.add(row)
        else:
            row.total_request += 1
            row.connect_key = os.urandom(5).hex()
            row.request_timestamps = [*(row.request_timestamps or []), now]

        if req_appr_mode == 0:
            row.joined_status = ExamRqStatus.STUDENT_PENDING_EXAM

        app_context.db.commit()
        app_context.db.refresh(row)
        if row.joined_status == ExamRqStatus.STUDENT_REQUEST_SEND:
            completed_count, joined_count, request_count = (
                await StudentRequestSession.get_with_is_joined(exam_id)
            )
            await ExamEventManager.push_exam_event(
                exam_id,
                [
                    5060,
                    {
                        "students": {
                            row.id: [row.student_name, row.roll_no, row.profile_image]
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
                        "STUDENT_REQUEST_SEND_COUNT": request_count,
                        "STUDENT_JOINED_EXAM_COUNT": joined_count,
                        "STUDENT_COMPLETED_EXAM_COUNT": completed_count,
                    },
                ],
            )

        return row

    @staticmethod
    async def connect(
        roll_no: int, connect_key: str, check_status=None
    ) -> Optional[ExamRequestSession]:
        await active_exam_db()

        record = SRSCache.get(roll_no)
        if record and record.connect_key == connect_key:
            return (
                await StudentRequestSession.is_valid(record) if check_status else record
            )

        record = (
            app_context.db.query(ExamRequestSession)
            .filter_by(roll_no=int(roll_no), connect_key=connect_key)
            .first()
        )

        if not record:
            return None

        record = StudentRequestSession._cache(record.to_dataclass())
        return await StudentRequestSession.is_valid(record) if check_status else record

    @staticmethod
    async def _get(
        exam_id: int, roll_no: int
    ) -> tuple[Optional[ExamRequestSession], list[ExamRequestSession]]:

        query = app_context.db.query(ExamRequestSession).filter_by(exam_id=int(exam_id))
        return (query.filter_by(roll_no=int(roll_no)).first(), query.all())

    @staticmethod
    async def getAll(*, limit: int = None, **filter) -> Optional[ExamRequestSession]:

        db = await active_exam_db()

        query = db.query(ExamRequestSession).filter_by(
            **{k: v for k, v in filter.items() if v is not None}
        )
        if limit is not None:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get(**filter) -> Optional[ExamRequestSession]:

        record = (
            app_context.db.query(ExamRequestSession)
            .filter_by(**{k: v for k, v in filter.items() if v is not None})
            .first()
        )

        return StudentRequestSession._cache(record.to_dataclass()) if record else None

    @staticmethod
    async def update(callback, **filter) -> Optional[ExamRequestSession]:
        """Active exam database"""
        await app_context.db.configure_exam()

        print("___student_update_requrst")
        if callable(callback) or isinstance(callback, _ExamRequestSession):
            query = app_context.db.query(ExamRequestSession)

            if callable(callback):
                row = query.filter_by(
                    **{k: v for k, v in filter.items() if v is not None}
                ).first()
                if row:
                    dt = await callback(row, query)
                    app_context.db.commit()
                    app_context.db.refresh(row)

                    return (
                        StudentRequestSession._cache(row.to_dataclass())
                        if isinstance(dt, ExamRequestSession)
                        else dt
                    )
                return None

            elif isinstance(callback, _ExamRequestSession):
                row = query.filter_by(id=callback.id).first()
                if row:
                    if row.joined_status in [
                        ExamRqStatus.BLOCK_IN_EXAM,
                        ExamRqStatus.REQUEST_REJECTED,
                        ExamRqStatus.STUDENT_REMOVED_FROM_EXAM,
                    ]:
                        return None

                    for field in fields(callback):
                        setattr(row, field.name, getattr(callback, field.name))
                    app_context.db.commit()
                    app_context.db.refresh(row)
                    return StudentRequestSession._cache(row.to_dataclass())

        return None

    @staticmethod
    async def delete(**filter) -> Optional[ExamRequestSession]:

        base = app_context.db.query(ExamRequestSession).filter_by(
            **{k: v for k, v in filter.items() if v is not None}
        )
        record = base.first()
        if record:
            cached = SRSCache.get(record.roll_no)
            if cached and cached.id == record.id:
                print("--------------------------delete", cached)
                SRSCache.pop(cached.roll_no, None)

        base.delete()
        app_context.db.commit()

        return record

    @staticmethod
    async def get_with_is_joined(
        exam_id: Optional[int],
        *,
        offset: int = 0,
        limit: int = 10,
        joined_record: bool = None,
    ):

        query = app_context.db.query(ExamRequestSession).filter(
            ExamRequestSession.exam_id == exam_id
        )

        def get_joined_statuses_data(statuses):
            return query.filter(ExamRequestSession.joined_status.in_(statuses))

        joined = get_joined_statuses_data(
            [
                ExamRqStatus.STUDENT_JOINED_EXAM,
                ExamRqStatus.STUDENT_PENDING_EXAM,
                ExamRqStatus.STUDENT_LEFT_EXAM,
            ]
        )

        joined_count = joined.count()

        request = get_joined_statuses_data(
            [
                ExamRqStatus.STUDENT_REQUEST_SEND,
                ExamRqStatus.REQUEST_REJECTED,
            ]
        )

        request_count = request.count()

        completed = get_joined_statuses_data([ExamRqStatus.STUDENT_COMPLETED_EXAM])
        completed_count = completed.count()

        if joined_record:
            students = {}
            result = []
            for record in joined.offset(offset).limit(limit).all():
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
            return students, result, joined_count, request_count

        return completed_count, joined_count, request_count
