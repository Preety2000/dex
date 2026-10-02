from sqlalchemy import desc
from dataclasses import dataclass, field

from includes.core.pagination import Pagination
from includes.core.request_filter import RequestFilter
from includes.utils.exm import convert_int_values
from includes.api.exam.results.results_conducted import IS_RESULTS
from includes.db.connection import active_exam_db
from includes.db.models.db_exam import (
    _ExamRecord,
    ExamDetails,
    ExamRecord,
    PracticeExamRecord,
    TeacherProfile,
)

from includes.db.models.utils import TimeStamp


class RecordType:
    STUDENT = 0
    INVIGILATOR = 1


@dataclass
class StudentCache:
    ById: dict = field(default_factory=dict)
    ByExam: dict = field(default_factory=dict)
    ByExamKey: dict = field(default_factory=dict)


STUDENT_CACHE = StudentCache()
INVIGILATOR_CACHE = StudentCache()


async def get_exam_details(record: _ExamRecord):
    if record.ts_info:
        info = record.ts_info.get("info")
        return {
            "rus_link": f"do/{record.key}",
            "exam_name": "Practice Series",
            "subject": [info[1]],
            "category": [info[2]],
            "timing": info[3],
        }

    else:
        db = await active_exam_db()
        controller_query = (
            db.query(ExamDetails).filter(ExamDetails.id == record.exam_id).first()
        )
        if not controller_query:
            return {}

        controller_info = (
            db.query(TeacherProfile)
            .filter(TeacherProfile.id == controller_query.teacher_id)
            .first()
        )

        details = convert_int_values(controller_query.details)
        time = all_qq = 0
        sub, cog = [], []

        for all_q, _sub, _cog, time_, *_ in details.values():
            time += time_
            all_qq += all_q
            sub.append(_sub)
            cog.append(_cog)

        return {
            "rus_link": record.key,
            "examinant": controller_info.name,
            "publish": controller_query.publish,
            "exam_name": controller_query.exam_name,
            "start_timestamp": controller_query.start_timestamp,
            "publish_timestamp": controller_query.publish_timestamp,
            "subject": sub,
            "category": cog,
            "qus_no": all_qq,
            "timing": time,
        }


async def get_result(record: _ExamRecord):

    exam_details = await get_exam_details(record)
    return {
        **exam_details,
        "key": record.key,
        "rus_no": f"NS{record.id:04}",
        "allmarks": record.allmarks,
        "timestamp": record.timestamp,
        "is_submitted": record.is_submitted,
        "submitted_on": record.submitted_on,
    }


class Student:

    @staticmethod
    def _cache_delete(record: _ExamRecord, record_type=RecordType.INVIGILATOR):
        cache, model = Student._catchmodel(record_type)

        cache.ById.pop(record.id, None)
        cache.ByExamKey.pop(record.key, None)
        cache.ByExam.pop((record.roll_no, record.exam_id), None)

        return record

    @staticmethod
    def _cache(record: _ExamRecord, cache: StudentCache):
        cache.ById[record.id] = record
        cache.ByExamKey[record.key] = record
        cache.ByExam[(record.roll_no, record.exam_id)] = record
        return record

    @staticmethod
    def _catchmodel(record_type=RecordType.STUDENT):
        if record_type == RecordType.INVIGILATOR:
            return INVIGILATOR_CACHE, ExamRecord

        return STUDENT_CACHE, PracticeExamRecord

    @staticmethod
    async def get(student_id: int, record_type=RecordType.STUDENT):
        cache, model = Student._catchmodel(record_type)

        record = cache.ById.get(student_id)
        if record:
            return record

        db = await active_exam_db()

        record = db.query(model).filter_by(id=student_id).first()
        if not record:
            return None
        return Student._cache(record.to_dataclass(), cache)

    @staticmethod
    async def get_by_exam_key(record_key: str, record_type=RecordType.STUDENT):
        cache, model = Student._catchmodel(record_type)

        record = cache.ByExamKey.get(record_key)
        if record:
            return record

        db = await active_exam_db()

        record = db.query(model).filter_by(key=record_key).first()
        if not record:
            return None
        return Student._cache(record.to_dataclass(), cache)

    @staticmethod
    async def get_by_exam(roll_no: int, exam_id: int, record_type=RecordType.STUDENT):
        cache, model = Student._catchmodel(record_type)
        record = cache.ByExam.get((roll_no, exam_id))
        if record:
            return record

        db = await active_exam_db()

        record = db.query(model).filter_by(roll_no=roll_no, exam_id=exam_id).first()

        if not record:
            return None
        return Student._cache(record.to_dataclass(), cache)

    @staticmethod
    async def insert(
        roll_no: int,
        exam_id: int,
        content,
    ):

        print("____student insurt data")
        record = INVIGILATOR_CACHE.ByExam.get((roll_no, exam_id))
        if record:
            return record.key

        db = await active_exam_db()

        record = (
            db.query(ExamRecord)
            .filter_by(
                roll_no=roll_no,
                exam_id=exam_id,
            )
            .first()
        )
        if not record:
            record = ExamRecord(
                roll_no=roll_no,
                exam_id=exam_id,
                content=content,
            )
            db.add(record)
            db.commit()
        db.refresh(record)
        Student._cache(
            record.to_dataclass(),
            INVIGILATOR_CACHE,
        )
        return record.key

    @staticmethod
    async def update(update_data: _ExamRecord, record_type=RecordType.STUDENT):
        cache, model = Student._catchmodel(record_type)

        db = await active_exam_db()

        record = (
            db.query(model)
            .filter_by(
                roll_no=update_data.roll_no,
                exam_id=update_data.exam_id,
            )
            .first()
        )

        if not record:
            return None

        record.content = update_data.content
        record.position = update_data.position
        record.pe_point = update_data.pe_point

        if update_data.is_submitted:
            record.submit_exam()
            data = await IS_RESULTS.get_result(update_data, True)
            try:
                record.allmarks = data[3][1]
            except:
                print("allmarks adding error")
                pass

        db.commit()
        db.refresh(record)
        return Student._cache(
            record.to_dataclass(),
            cache,
        )

    @staticmethod
    async def delete(key, roll_no, record_type=RecordType.STUDENT):
        db = await active_exam_db()

        cache, model = Student._catchmodel(record_type)
        record = (
            db.query(model).filter(model.roll_no == roll_no, model.key == key).first()
        )
        if not record:
            return None

        db.delete(record)
        db.commit()

        del cache.ById[record.id]
        del cache.ByExamKey[record.key]
        del cache.ByExam[(record.roll_no, record.exam_id)]

        return {"status": True}

    @staticmethod
    async def self_insert(roll_no, content, ts_info):
        db = await active_exam_db()

        query = (
            db.query(PracticeExamRecord)
            .filter_by(roll_no=roll_no)
            .order_by(desc(PracticeExamRecord.exam_id))
            .first()
        )
        count = query.exam_id + 1 if query else 1
        record = PracticeExamRecord(
            roll_no=roll_no,
            exam_id=count,
            content=content,
            ts_info=ts_info,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        Student._cache(
            record.to_dataclass(),
            STUDENT_CACHE,
        )
        return record.key

    @staticmethod
    async def has_submission_limit_exceeded(roll_no: int):
        db = await active_exam_db()

        start_ms, end_ms = TimeStamp._get_month_range()
        start_of_day, end_of_day = TimeStamp._get_day_range()

        base = db.query(PracticeExamRecord).filter(
            PracticeExamRecord.roll_no == roll_no
        )
        daily_count = base.filter(
            PracticeExamRecord.timestamp.between(start_of_day, end_of_day)
        ).count()
        monthly_count = base.filter(
            PracticeExamRecord.timestamp.between(start_ms, end_ms)
        ).count()
        return (daily_count >= 3, monthly_count >= 30)

    @staticmethod
    def get_period_query(base, model):
        # Today /This month /This year
        start_of_day, end_of_day = TimeStamp._get_day_range()
        start_ms, end_ms = TimeStamp._get_month_range()
        start_ys, end_ys = TimeStamp._get_year_range()

        return (
            base.filter(model.timestamp.between(start_of_day, end_of_day)),
            base.filter(model.timestamp.between(start_ms, end_ms)),
            base.filter(model.timestamp.between(start_ys, end_ys)),
        )

    @staticmethod
    async def get_submission_counts(
        roll_no: int,
        record_type=RecordType.STUDENT,
        *,
        limit: int = 100,
        page: int = 0,
        list_getter: bool = False,
        **more,
    ):
        db = await active_exam_db()

        cache, model = Student._catchmodel(record_type)
        base = await RequestFilter.apply_request_filters(
            model=model,
            request_type="referer",
            query=db.query(model).filter(model.roll_no == roll_no),
            columns={"roll_no": "rollno"},
            search_columns=["exam_id", "roll_no"],
        )

        daily, monthly, yearly = Student.get_period_query(base, model)

        total = base.count()

        pagination = Pagination("referer")
        await pagination.load(limit=limit)
        offset = pagination.get_offset()

        exam_list = []
        _pagination = None
        if list_getter:
            records = (
                base.order_by(model.timestamp.desc())
                .offset(offset)
                .limit(pagination.limit)
                .all()
            )

            async def enrich_student(record):
                return await get_result(Student._cache(record.to_dataclass(), cache))

            exam_list, _pagination, total = await pagination.paginate(
                total=total,
                data=records,
                transform=enrich_student,
            )

        return (
            exam_list,
            _pagination,
            daily.count(),
            monthly.count(),
            yearly.count(),
            total,
        )
