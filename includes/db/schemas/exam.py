from datetime import datetime
from uuid import UUID, uuid4
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field

# Helper function for default UUID string generation
def generate_uuid_str() -> str:
    return str(uuid4())


# 1. TeacherProfile Schemas

class TeacherProfileBase(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    img: Optional[str] = Field(None, max_length=255)
    signature: Optional[str] = Field(None, max_length=255)
    biography: Optional[str] = Field(None, max_length=255)
    join_mode: Optional[int] = None
    open_request: Optional[int] = None
    req_appr_mode: Optional[int] = None
    result_visibility: Optional[int] = None
    exam_category: List[Any] = Field(default_factory=list)
    student_limit: int = 250

class TeacherProfileCreate(TeacherProfileBase):
    pass

class TeacherProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    img: Optional[str] = Field(None, max_length=255)
    signature: Optional[str] = Field(None, max_length=255)
    biography: Optional[str] = Field(None, max_length=255)
    join_mode: Optional[int] = None
    open_request: Optional[int] = None
    req_appr_mode: Optional[int] = None
    result_visibility: Optional[int] = None
    exam_category: Optional[List[Any]] = None
    student_limit: Optional[int] = None

class TeacherProfileResponse(TeacherProfileBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


# 2. ExamDetails Schemas

class ExamDetailsBase(BaseModel):
    teacher_id: int
    exam_name: Optional[str] = None
    exam_category: Optional[str] = None
    details: List[Any] = Field(default_factory=list)
    questions: List[Any] = Field(default_factory=list)
    notification: bool = False
    join_mode: Optional[int] = None
    open_request: Optional[int] = None
    req_appr_mode: Optional[int] = None
    result_visibility: Optional[int] = None
    publish: bool = False
    start_timestamp: Optional[datetime] = None
    publish_timestamp: Optional[datetime] = None

class ExamDetailsCreate(ExamDetailsBase):
    keys: str = Field(default_factory=generate_uuid_str)

class ExamDetailsUpdate(BaseModel):
    exam_name: Optional[str] = None
    exam_category: Optional[str] = None
    details: Optional[List[Any]] = None
    questions: Optional[List[Any]] = None
    notification: Optional[bool] = None
    join_mode: Optional[int] = None
    open_request: Optional[int] = None
    req_appr_mode: Optional[int] = None
    result_visibility: Optional[int] = None
    publish: Optional[bool] = None
    start_timestamp: Optional[datetime] = None
    publish_timestamp: Optional[datetime] = None

class ExamDetailsResponse(ExamDetailsBase):
    id: int
    keys: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# 3. ExamRequestSession Schemas

class ExamRequestSessionBase(BaseModel):
    roll_no: int
    student_name: str
    profile_image: str
    vi_key: Optional[str] = None
    has_key: Optional[str] = None
    srec_kry: Optional[str] = None
    connect_key: Optional[str] = None
    exam_id: int
    teacher_id: Optional[int] = None
    is_joined: Optional[bool] = False
    is_re_requested: bool = False
    joined_status: int = 0
    total_request: int = 0
    total_exam_joins: int = 0
    request_timestamps: List[Any] = Field(default_factory=list)
    join_timestamps: List[Any] = Field(default_factory=list)
    leave_timestamps: List[Any] = Field(default_factory=list)
    removed_timestamps: List[Any] = Field(default_factory=list)

class ExamRequestSessionCreate(ExamRequestSessionBase):
    pass

class ExamRequestSessionUpdate(BaseModel):
    student_name: Optional[str] = None
    profile_image: Optional[str] = None
    is_joined: Optional[bool] = None
    is_re_requested: Optional[bool] = None
    joined_status: Optional[int] = None
    total_request: Optional[int] = None
    total_exam_joins: Optional[int] = None
    request_timestamps: Optional[List[Any]] = None
    join_timestamps: Optional[List[Any]] = None
    leave_timestamps: Optional[List[Any]] = None
    removed_timestamps: Optional[List[Any]] = None

class ExamRequestSessionResponse(ExamRequestSessionBase):
    id: int
    started_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 4. ExamRecord Schemas

class ExamRecordBase(BaseModel):
    roll_no: int
    exam_id: int
    pe_point: Optional[str] = Field(None, max_length=255)
    position: int = 0
    ts_info: List[Any] = Field(default_factory=list)
    content: List[Any] = Field(default_factory=list)
    allmarks: float = 0.0
    is_submitted: bool = False
    submitted_on: Optional[datetime] = None

class ExamRecordCreate(ExamRecordBase):
    key: str = Field(default_factory=generate_uuid_str)

class ExamRecordUpdate(BaseModel):
    pe_point: Optional[str] = Field(None, max_length=255)
    position: Optional[int] = None
    ts_info: Optional[List[Any]] = None
    content: Optional[List[Any]] = None
    allmarks: Optional[float] = None
    is_submitted: Optional[bool] = None
    submitted_on: Optional[datetime] = None

class ExamRecordResponse(ExamRecordBase):
    id: int
    key: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# 5. PracticeExamRecord Schemas

class PracticeExamRecordBase(BaseModel):
    roll_no: int
    exam_id: int
    pe_point: Optional[str] = Field(None, max_length=255)
    position: int = 0
    content: List[Any] = Field(default_factory=list)
    ts_info: List[Any] = Field(default_factory=list)
    allmarks: float = 0.0
    is_submitted: bool = False
    submitted_on: Optional[datetime] = None

class PracticeExamRecordCreate(PracticeExamRecordBase):
    key: str = Field(default_factory=generate_uuid_str)

class PracticeExamRecordUpdate(BaseModel):
    pe_point: Optional[str] = Field(None, max_length=255)
    position: Optional[int] = None
    content: Optional[List[Any]] = None
    ts_info: Optional[List[Any]] = None
    allmarks: Optional[float] = None
    is_submitted: Optional[bool] = None
    submitted_on: Optional[datetime] = None

class PracticeExamRecordResponse(PracticeExamRecordBase):
    id: int
    key: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# 6. StudentTeacherAssociation Schemas

class StudentTeacherAssociationBase(BaseModel):
    st_roll_no: int
    teacher_id: int
    exam_category: List[Any] = Field(default_factory=list)
    link_status: int = 1

class StudentTeacherAssociationCreate(StudentTeacherAssociationBase):
    pass

class StudentTeacherAssociationUpdate(BaseModel):
    exam_category: Optional[List[Any]] = None
    link_status: Optional[int] = None

class StudentTeacherAssociationResponse(StudentTeacherAssociationBase):
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)