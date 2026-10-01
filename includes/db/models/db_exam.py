# Standard Library
import os
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, List, Optional

# Third-Party
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base

# Local Imports
from includes.db.dataclass import ExamRqStatus
from includes.db.models.utils import JsonList, TimeStamp


def generate_uuid():
    return str(uuid.uuid4())


def generate_connect_key():
    return os.urandom(5).hex()


ExamDb = declarative_base()


# TEACHER PROFILE
@dataclass
class _TeacherProfile:
    id: Optional[int] = None
    name: Optional[str] = None
    img: Optional[str] = None
    signature: Optional[str] = None
    biography: Optional[str] = None

    join_mode: Optional[int] = None
    open_request: Optional[int] = None
    req_appr_mode: Optional[int] = None
    result_visibility: Optional[int] = None

    exam_category: List = field(default_factory=list)
    student_limit: int = 250
    timestamp: TimeStamp = field(default_factory=TimeStamp.now_iso)

    def to_dict(self):
        return asdict(self)


class TeacherProfile(ExamDb):
    __tablename__ = "teacher_profile"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    img = Column(String(255))
    signature = Column(String(255))
    biography = Column(String(255))

    join_mode = Column(Integer)
    open_request = Column(Integer)
    req_appr_mode = Column(Integer)
    result_visibility = Column(Integer)

    exam_category = Column(JsonList)
    student_limit = Column(Integer, default=250)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    def to_dataclass(self) -> _TeacherProfile:
        return _TeacherProfile(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )


# EXAM DETAILS
@dataclass
class _ExamDetails:
    id: Optional[int] = None
    keys: str = field(default_factory=generate_uuid)
    teacher_id: int = 0
    exam_name: Optional[str] = None
    exam_category: Optional[str] = None
    details: List = field(default_factory=list)
    questions: List = field(default_factory=list)
    notification: bool = False
    join_mode: Optional[int] = None
    open_request: Optional[int] = None
    req_appr_mode: Optional[int] = None
    result_visibility: Optional[int] = None
    publish: bool = False
    start_timestamp: Optional[int] = None
    publish_timestamp: Optional[int] = None
    timestamp: TimeStamp = field(default_factory=TimeStamp.now_iso)

    teacher_record: Optional[List] = None


class ExamDetails(ExamDb):
    __tablename__ = "exam_details"

    id = Column(Integer, primary_key=True, unique=True)
    keys = Column(String(36), default=generate_uuid, unique=True)
    teacher_id = Column(Integer, nullable=False)
    exam_name = Column(Text)
    exam_category = Column(Text, nullable=True)
    details = Column(JsonList)
    questions = Column(JsonList)
    notification = Column(Boolean, default=False)
    join_mode = Column(Integer)
    open_request = Column(Integer)
    req_appr_mode = Column(Integer)
    result_visibility = Column(Integer)
    publish = Column(Boolean, default=False)
    start_timestamp = Column(TimeStamp, nullable=True)
    publish_timestamp = Column(TimeStamp, nullable=True)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    def to_dataclass(self) -> _ExamDetails:
        return _ExamDetails(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )


# EXAM REQUEST SESSION
@dataclass
class _ExamRequestSession:
    id: Optional[int] = None
    roll_no: Optional[int] = None
    student_name: Optional[str] = None
    profile_image: Optional[str] = None

    user_id: Optional[str] = None
    exam_id: Optional[int] = None
    teacher_id: Optional[int] = None

    vi_key: Optional[str] = None
    has_key: Optional[str] = None
    srec_kry: Optional[str] = None
    connect_key: Optional[str] = field(default_factory=generate_connect_key)

    is_joined: bool = False
    is_re_requested: bool = False

    joined_status: int = 0
    total_request: int = 0
    total_exam_joins: int = 0

    request_timestamps: Optional[List[Any]] = field(default_factory=list)
    join_timestamps: Optional[List[Any]] = field(default_factory=list)
    leave_timestamps: Optional[List[Any]] = field(default_factory=list)
    removed_timestamps: Optional[List[Any]] = field(default_factory=list)

    started_at: Optional[int] = None


class ExamRequestSession(ExamDb):
    __tablename__ = "exam_rq_session"

    id = Column(Integer, primary_key=True, autoincrement=True)

    roll_no = Column(BigInteger, nullable=False, index=True)
    student_name = Column(Text, nullable=False)
    profile_image = Column(Text, nullable=False)

    vi_key = Column(Text, nullable=True)
    has_key = Column(Text, nullable=True)
    srec_kry = Column(Text, nullable=True)
    connect_key = Column(Text, nullable=True)

    exam_id = Column(BigInteger, nullable=False, index=True)
    teacher_id = Column(BigInteger, nullable=True)

    is_joined = Column(Boolean, default=False, nullable=True)
    is_re_requested = Column(Boolean, default=False, nullable=False)

    joined_status = Column(
        Integer, default=ExamRqStatus.STUDENT_REQUEST_SEND, nullable=False
    )
    total_request = Column(Integer, default=0, nullable=False)
    total_exam_joins = Column(Integer, default=0, nullable=False)

    request_timestamps = Column(JsonList, default=list)
    join_timestamps = Column(JsonList, default=list)
    leave_timestamps = Column(JsonList, default=list)
    removed_timestamps = Column(JsonList, default=list)

    started_at = Column(TimeStamp, default=TimeStamp.now_iso)

    __table_args__ = (
        UniqueConstraint("roll_no", "exam_id", name="uq_exam_registration"),
    )

    def to_dataclass(self) -> _ExamRequestSession:
        return _ExamRequestSession(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )


# EXAM RECORD
@dataclass
class _ExamRecord:
    id: Optional[int] = None
    key: str = field(default_factory=generate_uuid)

    roll_no: int = 0
    exam_id: int = 0

    pe_point: Optional[str] = None
    position: int = 0

    ts_info: List[Any] = field(default_factory=list)
    content: List[Any] = field(default_factory=list)

    allmarks: float = 0.0

    is_submitted: bool = False
    submitted_on: Optional[int] = None

    timestamp: TimeStamp = field(default_factory=TimeStamp.now_iso)


class ExamRecord(ExamDb):
    __tablename__ = "st_exam_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(36), default=generate_uuid, unique=True)

    roll_no = Column(BigInteger, nullable=False)
    exam_id = Column(Integer, nullable=False)
    pe_point = Column(String(255), default=None)
    position = Column(Integer, default=0)
    ts_info = Column(JsonList, default=list)
    content = Column(JsonList, nullable=False)
    allmarks = Column(Float, default=0)
    is_submitted = Column(Boolean, default=False)
    submitted_on = Column(TimeStamp, nullable=True)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    __table_args__ = (UniqueConstraint("roll_no", "exam_id", name="uq_student_examid"),)

    def submit_exam(self) -> None:
        """Mark the exam as submitted and store submission epoch timestamp."""
        if self.is_submitted:
            raise ValueError("Exam already submitted.")

        self.is_submitted = True
        self.submitted_on = TimeStamp.now_iso()

    def to_dataclass(self) -> _ExamRecord:
        return _ExamRecord(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )


class PracticeExamRecord(ExamDb):
    __tablename__ = "st_pte_exam_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(36), default=generate_uuid, unique=True)

    roll_no = Column(BigInteger, nullable=False)
    exam_id = Column(Integer, nullable=False)
    pe_point = Column(String(255), default=None)
    position = Column(Integer, default=0)
    content = Column(JsonList, nullable=False)
    ts_info = Column(JsonList, nullable=False)
    allmarks = Column(Float, default=0)
    is_submitted = Column(Boolean, default=False)
    submitted_on = Column(TimeStamp, nullable=True)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    __table_args__ = (UniqueConstraint("roll_no", "exam_id", name="uq_stu_emid"),)

    def submit_exam(self) -> None:
        """Mark the exam as submitted and store submission epoch timestamp."""
        if self.is_submitted:
            raise ValueError("Exam already submitted.")

        self.is_submitted = True
        self.submitted_on = TimeStamp.now_iso()

    def to_dataclass(self) -> _ExamRecord:
        return _ExamRecord(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )


# STUDENT TEACHER ASSOCIATION
@dataclass
class _StudentTeacherAssociation:
    st_roll_no: Optional[int] = None
    teacher_id: Optional[int] = None
    link_status: Optional[int] = None

    exam_category: List[Any] = field(default_factory=list)
    timestamp: Optional[int] = None


class StudentTeacherAssociation(ExamDb):
    __tablename__ = "st_links"

    st_roll_no = Column(BigInteger, primary_key=True)
    teacher_id = Column(BigInteger, primary_key=True)
    exam_category = Column(JsonList, default=list)
    link_status = Column(Integer, default=1)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    __table_args__ = (
        UniqueConstraint("st_roll_no", "teacher_id", name="uq_st_roll_no_teacher"),
    )

    def to_dataclass(self) -> _StudentTeacherAssociation:
        return _StudentTeacherAssociation(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )
