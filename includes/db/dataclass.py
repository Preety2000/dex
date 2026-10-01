from datetime import date, datetime
from dataclasses import dataclass, field, fields, is_dataclass
from collections.abc import Mapping, Sequence
from enum import IntEnum
from sqlalchemy.inspection import inspect

class ExamRqStatus(IntEnum):
    STUDENT_REQUEST_SEND = 0        # Request sent from student to examiner
    REQUEST_REJECTED = 1
    STUDENT_PENDING_EXAM = 2        # Request accepted by examiner and pending exam
    STUDENT_JOINED_EXAM = 3
    STUDENT_LEFT_EXAM = 4
    STUDENT_REMOVED_FROM_EXAM = 5
    STUDENT_COMPLETED_EXAM = 6
    BLOCK_IN_EXAM = 7


class TeacherStatus(IntEnum):
    PENDING = 0
    VERIFIED = 1
    UNVERIFIED = 2
    BLOCKED = 3
    TRY_AGAIN = 4

class MemberRole(IntEnum):
    PENDING = 0
    STUDENT = 1
    TEACHER = 2
    BLOCKED = 3
    TRYMORE = 4


def datetime_to_unix(dt: datetime) -> int:
    return int(dt.timestamp())


def serialize(obj, visited=None):
    """
    Recursively convert Python objects into JSON-serializable structures.
    Handles: datetime, dataclass, ORM, dict, list, tuple.
    """

    if obj is None:
        return None

    if visited is None:
        visited = set()

    # prevent infinite recursion (ORM circular refs)
    if isinstance(obj, object) and not isinstance(obj, (str, int, float, bool)):
        obj_id = id(obj)
        if obj_id in visited:
            return None
        
        visited.add(obj_id)

    # datetime
    if isinstance(obj, datetime):
        return obj.isoformat()
    
    if isinstance(obj, date):
        return obj.isoformat()

    # dataclass
    if is_dataclass(obj):
        return {
            f.name: serialize(getattr(obj, f.name), visited)
            for f in fields(obj)
        }

    # SQLAlchemy ORM
    try:
        mapper = inspect(obj)
        data = {
            attr.key: serialize( getattr(obj, attr.key), visited)
            for attr in mapper.mapper.attrs
        }
        for prop in ["img", "url"]:
            if hasattr(obj, prop):
                data[prop] = getattr(obj, prop)
                
        return data
    except:
        pass

    # dict / mapping
    if isinstance(obj, Mapping):
        return {k: serialize(v, visited) for k, v in obj.items()}

    # list / tuple / set
    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        return [serialize(i, visited) for i in obj]

    # fallback primitive
    return obj



from typing import Any, Optional



def to_dict(obj):
    if is_dataclass(obj):
        return {
            f.name: to_dict( getattr(obj, f.name) ) 
            for f in fields(obj)
        }

    # list of items
    if isinstance(obj, list):
        return [to_dict(i) for i in obj]

    # dict support (optional safety)
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}

    # primitive value
    return obj

  
@dataclass
class _MemberSession:
    id: Optional[int] = None
    user_id: int = 0
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    is_active: bool = False
    login_time: Optional[datetime] = None
    logout_time: Optional[datetime] = None

@dataclass
class _Subject:
    id: int = 0
    name: str = ""
    slug: str = ""
    used: int = 0
    content: str = ""
    
@dataclass
class _Terms:
    id: int 
    resource: int
    name: str
    image_src: str
    slug: str
    topic: int
    subject_id: Optional[int]
    description: str
    used: Optional[int]
    
    img: str = ""
    url: str = ""
        
    mcq_count: int = 0
    first_mcq: Any = None
    article_count: int= 0
    first_article:Any = None
    
@dataclass
class _QuizQuestion:
    id: Optional[int] = None
    question: str = ""
    excerpt: str = ""
    correct_answer: str = ""
    incorrect_answers: str = ""
    subject_id: int = 0
    status: str = ""
    views: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    options: list[str] = None
    
    url: str = None
    term: _Terms = None
    category: list[_Terms] = field(default_factory=list)
    
    prev_quiz: str = None
    next_quiz: str = None
    
@dataclass
class _PostsMetaTags:
    id: int = 0
    subject: int = None 
    excerpt: str = ""
    tags_group: list[str] = field(default_factory=list)
    secret_key: str = None


@dataclass
class _Suggestion:
    id: int
    views: int
    query_id: int
    tags: str
    most_used: int = 0
    
@dataclass
class _Article:
    id: int = 0
    title: str = ""
    slug: str = ""
    parameter: Optional[int] = None
    content: str = ""
    timestamp: datetime = datetime.utcnow()
    update_timestamp: datetime = datetime.utcnow()
    thumbnail: Optional[str] = None
    status: Optional[str] = None
    comment_status: Optional[str] = None
    type: int = 0
    mdata: _PostsMetaTags | dict = None
    
    date: str = None
    likes: int = None
    feedback: str = "feedback"
    category: list[_Terms] = field(default_factory=list)
    
    url: str = None
    excerpt: str = None
    subject: list[_Subject] = None
    secret_key: str = None
    suggestion: list[str] = field(default_factory=list)
    prev_article: Any = None
    next_article: Any = None
    
