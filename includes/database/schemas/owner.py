from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Subject Schemas
class SubjectBase(BaseModel):
    name: str = Field(..., max_length=255, description="Subject name")
    slug: str = Field(..., max_length=255, description="URL friendly slug")
    used: int = Field(default=0, description="Usage counter")
    content: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    used: Optional[int] = None
    content: Optional[str] = None

class SubjectResponse(SubjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Analytics Schemas
class AnalyticsBase(BaseModel):
    query_id: int
    time: int
    referrer: str
    meta: str

class AnalyticsCreate(AnalyticsBase):
    pass

class AnalyticsResponse(AnalyticsBase):
    id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)


# AnalyticsQuery Schemas
class AnalyticsQueryBase(BaseModel):
    title: str
    path: str

class AnalyticsQueryCreate(AnalyticsQueryBase):
    pass

class AnalyticsQueryResponse(AnalyticsQueryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# VerifyIdentity Schemas
class VerifyIdentityBase(BaseModel):
    user_id: Optional[int] = None
    subject: Optional[str] = None
    experience: Optional[str] = None
    document: Optional[str] = None
    document_name: Optional[str] = None
    info: Optional[str] = None
    status: int = Field(default=0, description="TeacherStatus enum value")
    reasons: Optional[str] = ""
    reject_message: List[Any] = Field(default_factory=list)

class VerifyIdentityCreate(VerifyIdentityBase):
    user_id: int

class VerifyIdentityUpdate(BaseModel):
    subject: Optional[str] = None
    experience: Optional[str] = None
    document: Optional[str] = None
    document_name: Optional[str] = None
    info: Optional[str] = None
    status: Optional[int] = None
    reasons: Optional[str] = None
    reject_message: Optional[List[Any]] = None
    verify_timestamp: Optional[datetime] = None

class VerifyIdentityResponse(VerifyIdentityBase):
    id: int
    timestamp: datetime
    verify_timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# MemberSession Schemas
class MemberSessionBase(BaseModel):
    user_id: int
    device_id: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=255)
    is_active: bool = False

class MemberSessionCreate(MemberSessionBase):
    pass

class MemberSessionResponse(MemberSessionBase):
    id: int
    login_time: datetime
    logout_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Members Schemas
class MembersBase(BaseModel):
    name: str = Field(..., max_length=255)
    username: str = Field(..., max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    image_src: Optional[str] = "image.png"
    biography: Optional[str] = None
    loginfo: Optional[str] = None
    secret: Optional[str] = None
    ipinfo: Optional[str] = None
    device: List[Any] = Field(default_factory=list)
    gender: int = 0
    reg_no: Optional[int] = None
    status: int = Field(default=0, description="MemberRole enum value")

class MembersCreate(MembersBase):
    password: str = Field(..., min_length=6, description="Plaintext password")

class MembersUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    image_src: Optional[str] = None
    biography: Optional[str] = None
    loginfo: Optional[str] = None
    secret: Optional[str] = None
    ipinfo: Optional[str] = None
    device: Optional[List[Any]] = None
    gender: Optional[int] = None
    status: Optional[int] = None

class MembersResponse(MembersBase):
    id: int
    tk_id: UUID
    timestamp: datetime
    identity: Optional[VerifyIdentityResponse] = None
    model_config = ConfigDict(from_attributes=True)


# OwnerUser (AdminUser) Schemas
class OwnerUserBase(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=255)
    token: Optional[str] = None
    ipinfo: Optional[str] = None

class OwnerUserCreate(OwnerUserBase):
    email: EmailStr
    password: str = Field(..., min_length=6)

class OwnerUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    token: Optional[str] = None
    ipinfo: Optional[str] = None

class OwnerUserResponse(OwnerUserBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# Backup Schemas
class BackupBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: List[Any] = Field(default_factory=list)
    types: str = Field(..., max_length=100)

class BackupCreate(BackupBase):
    pass

class BackupResponse(BackupBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)