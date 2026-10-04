import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Integer,
    String,
    Text,
    func,
    select,
    text,
)
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from includes.database.base import BaseOwner
from includes.core.globals.entry import app_context
from includes.database.dataclass.dataclass import _Subject, _MemberSession, MemberRole, TeacherStatus, serialize
from includes.database.models.utils import TimeStamp, JsonList


class Subject(BaseOwner):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    used = Column(Integer, default=0)
    content = Column(Text, nullable=True)

    def to_dataclass(self) -> _Subject:
        return _Subject(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )


class Analytics(BaseOwner):
    __tablename__ = "analytics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, nullable=False)
    time = Column(Integer, nullable=False)
    referrer = Column(Text, nullable=False)
    meta = Column(Text, nullable=False)
    date = Column(TimeStamp, default=TimeStamp.now_iso)


class AnalyticsQuery(BaseOwner):
    __tablename__ = "analytics_query"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    path = Column(Text, nullable=False)


class VerifyIdentity(BaseOwner):
    __tablename__ = "verify_indentity"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True)
    subject = Column(Text)
    experience = Column(Text)
    document = Column(Text)
    document_name = Column(Text)
    info = Column(Text, nullable=True)
    status = Column(Integer, default=TeacherStatus.PENDING)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    reasons = Column(Text, default="")
    reject_message = Column(JsonList, default=list)
    verify_timestamp = Column(TimeStamp, nullable=True)


class Members(BaseOwner):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tk_id = Column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    image_src = Column(String(255), default="image.png")
    biography = Column(Text, nullable=True)
    password = Column(Text, nullable=False)
    loginfo = Column(Text, nullable=True)
    secret = Column(Text, nullable=True)
    ipinfo = Column(Text, nullable=True)
    device = Column(JsonList, nullable=False)
    gender = Column(Integer, default=0)
    reg_no = Column(Integer, nullable=True)
    status = Column(Integer, default=MemberRole.PENDING)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    identity = relationship(
        "VerifyIdentity",
        primaryjoin="Members.id == foreign(VerifyIdentity.user_id)",
        uselist=False,
    )    
    async def to_dataclass(self):
        data = serialize(self)
        db = await app_context.db.configure_main()
        session = select(MemberSession).where(MemberSession.user_id == self.id)
        data["last_login"] = serialize(db.execute(session).scalars().first())
        return data


    def generate_password(self, password, option):
        query = "pbkdf2:sha256:600000$"
        query2 = "scrypt:32768:8:1$"
        query_secound = "SZMTWS_"
        query_secound2 = "SZMTWS3_"
        if option == True:
            password = password.replace(query_secound, query)
            password = password.replace(query_secound2, query2)
        else:
            password = password.replace(query, query_secound)
            password = password.replace(query2, query_secound2)
        return password

    def set_password(self, password):
        self.password = self.generate_password(generate_password_hash(password), False)

    def check_password(self, password):
        if not password:
            return password
        return check_password_hash(
            self.generate_password(self.password, True), password
        )


class MemberSession(BaseOwner):
    __tablename__ = "member_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    device_id = Column(Text)
    ip_address = Column(String(255))
    is_active = Column(Boolean, nullable=False, default=False)
    login_time = Column(TimeStamp, default=TimeStamp.now_iso)
    logout_time = Column(TimeStamp, nullable=True)

    def to_dataclass(self) -> _MemberSession:
        return _MemberSession(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )


class OwnerUser(BaseOwner):
    __tablename__ = "adminuser"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    phone = Column(String(255))
    password = Column(Text)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)
    token = Column(Text)
    ipinfo = Column(Text)

    def generate_password(self, password, option):
        query = "pbkdf2:sha256:600000$"
        query_secound = "SZMTWS_"
        if option == True:
            password = password.replace(query_secound, query)
        else:
            password = password.replace(query, query_secound)
        return password

    def set_password(self, password):
        self.password = self.generate_password(generate_password_hash(password), False)

    def check_password(self, password):
        return check_password_hash(
            self.generate_password(self.password, True), password
        )


class Beckup(BaseOwner):
    __tablename__ = "backup"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(JsonList, nullable=False)
    types = Column(String(100), nullable=False)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)


def bindOwnerModelsToSession(session):
    session.backup = session.query(Beckup)
    session.member = session.query(Members)
    session.subject = session.query(Subject)
    session.analytics = session.query(Analytics)
    session.MemberSession = session.query(MemberSession)
    session.analyticsquery = session.query(AnalyticsQuery)
    session.verifyindentity = session.query(VerifyIdentity)
    return session
