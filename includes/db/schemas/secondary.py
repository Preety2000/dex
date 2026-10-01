from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

# 1. Books Schemas

class BooksBase(BaseModel):
    name: Optional[str] = None
    excerpt: Optional[str] = None
    writer: Optional[int] = None
    subject: Optional[int] = None
    image_src: Optional[str] = None
    slug: Optional[str] = None

class BooksCreate(BooksBase):
    name: str

class BooksUpdate(BaseModel):
    name: Optional[str] = None
    excerpt: Optional[str] = None
    writer: Optional[int] = None
    subject: Optional[int] = None
    image_src: Optional[str] = None
    slug: Optional[str] = None

class BooksResponse(BooksBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# 2. Writers Schemas

class WritersBase(BaseModel):
    name: Optional[str] = None
    excerpt: Optional[str] = None
    slug: Optional[str] = None

class WritersCreate(WritersBase):
    name: str

class WritersUpdate(BaseModel):
    name: Optional[str] = None
    excerpt: Optional[str] = None
    slug: Optional[str] = None

class WritersResponse(WritersBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# 3. BooksRelationship Schemas

class BooksRelationshipBase(BaseModel):
    books_id: int
    terms_id: int

class BooksRelationshipCreate(BooksRelationshipBase):
    pass

class BooksRelationshipResponse(BooksRelationshipBase):
    model_config = ConfigDict(from_attributes=True)


class PagesInsideBase(BaseModel):
    title: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    types: int
    content: str

class PagesInsideCreate(PagesInsideBase):
    pass

class PagesInsideUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    types: Optional[int] = None
    content: Optional[str] = None

class PagesInsideResponse(PagesInsideBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# 5. University Schemas

class UniversityBase(BaseModel):
    name: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    used: int

class UniversityCreate(UniversityBase):
    pass

class UniversityUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    used: Optional[int] = None

class UniversityResponse(UniversityBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# 6. Syllabus Schemas

class SyllabusBase(BaseModel):
    title: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    subject: str = Field(..., max_length=100)
    university: int
    content: str

class SyllabusCreate(SyllabusBase):
    pass

class SyllabusUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    subject: Optional[str] = Field(None, max_length=100)
    university: Optional[int] = None
    content: Optional[str] = None

class SyllabusResponse(SyllabusBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# 7. Courses Schemas

class CoursesBase(BaseModel):
    title: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    university: int
    content: str

class CoursesCreate(CoursesBase):
    pass

class CoursesUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    university: Optional[int] = None
    content: Optional[str] = None

class CoursesResponse(CoursesBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# 8. Jobs Schemas

class JobsBase(BaseModel):
    title: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    types: int
    admitcard: int
    content: str
    lastsate: datetime

class JobsCreate(JobsBase):
    pass

class JobsUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    types: Optional[int] = None
    admitcard: Optional[int] = None
    content: Optional[str] = None
    lastsate: Optional[datetime] = None

class JobsResponse(JobsBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# 9. Terms Schemas

class TermsBase(BaseModel):
    slug: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    image_src: str = "empty.png"
    resource: int
    topic: int
    subject_id: Optional[int] = None
    description: str
    used: int = 0

class TermsCreate(TermsBase):
    pass

class TermsUpdate(BaseModel):
    slug: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    image_src: Optional[str] = None
    resource: Optional[int] = None
    topic: Optional[int] = None
    subject_id: Optional[int] = None
    description: Optional[str] = None
    used: Optional[int] = None

class TermsCategoryItem(BaseModel):
    id: int
    url: str
    img: str
    used: int
    name: str
    mcq_count: Optional[int] = 0
    description: str

class TermsResponse(TermsBase):
    id: int
    img: str
    url: str
    mcq_count: Optional[int] = 0
    article_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


# 10. QuizQuestion Schemas

class QuizQuestionBase(BaseModel):
    question: str
    excerpt: str
    correct_answer: str
    incorrect_answers: List[Any] = Field(default_factory=list, description="Parsed from MCQJsonList")
    subject_id: int
    status: str = Field(..., max_length=100)
    views: int = 0

class QuizQuestionCreate(QuizQuestionBase):
    pass

class QuizQuestionUpdate(BaseModel):
    question: Optional[str] = None
    excerpt: Optional[str] = None
    correct_answer: Optional[str] = None
    incorrect_answers: Optional[List[Any]] = None
    subject_id: Optional[int] = None
    status: Optional[str] = Field(None, max_length=100)
    views: Optional[int] = None

class QuizQuestionResponse(QuizQuestionBase):
    id: int
    timestamp: datetime
    url: Optional[str] = None
    category: Optional[List[TermsCategoryItem]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# 11. QuizRelationships & TermsRelationship

class QuizRelationshipsBase(BaseModel):
    terms_id: int
    quiz_id: int

class QuizRelationshipsResponse(QuizRelationshipsBase):
    model_config = ConfigDict(from_attributes=True)


class TermsRelationshipBase(BaseModel):
    article_id: int
    terms_id: int
    is_type: Optional[int] = None
    is_order: int

class TermsRelationshipResponse(TermsRelationshipBase):
    model_config = ConfigDict(from_attributes=True)


# 12. ArticleMetadata Schemas

class ArticleMetadataBase(BaseModel):
    subject_id: Optional[int] = None
    excerpt: str
    tags_group: List[Any] = Field(default_factory=list)
    secret_key: Optional[str] = None

class ArticleMetadataCreate(ArticleMetadataBase):
    id: int

class ArticleMetadataResponse(ArticleMetadataBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# 13. Article Schemas

class ArticleBase(BaseModel):
    title: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    parameter: Optional[int] = None
    content: str
    thumbnail: Optional[str] = None
    status: Optional[str] = Field(None, max_length=255)
    comment_status: Optional[str] = Field(None, max_length=100)
    type: int

class ArticleCreate(ArticleBase):
    mdata: Optional[ArticleMetadataBase] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    parameter: Optional[int] = None
    content: Optional[str] = None
    views: Optional[int] = None
    thumbnail: Optional[str] = None
    status: Optional[str] = None
    comment_status: Optional[str] = None
    type: Optional[int] = None

class ArticleResponse(ArticleBase):
    id: int
    timestamp: datetime
    update_timestamp: datetime
    mdata: Optional[ArticleMetadataResponse] = None
    prev_article: Optional[Dict[str, Any]] = None
    next_article: Optional[Dict[str, Any]] = None
    likes: Optional[int] = None
    category: Optional[List[TermsResponse]] = None

    model_config = ConfigDict(from_attributes=True)


# 14. Suggestion Schemas

class SuggestionBase(BaseModel):
    views: int
    query_id: int
    tags: str = Field(..., max_length=255)
    most_used: int = 0

class SuggestionCreate(SuggestionBase):
    pass

class SuggestionResponse(SuggestionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# 15. UserRelationships & Trending Schemas

class UserRelationshipsBase(BaseModel):
    article_id: int
    users_id: int

class UserRelationshipsResponse(UserRelationshipsBase):
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class TrendingBase(BaseModel):
    id: int
    question: int
    trending: int

class TrendingResponse(TrendingBase):
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# 16. Backup Schemas (Secondary DB)

class BeckupSecondaryBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    types: str = Field(..., max_length=100)

class BeckupSecondaryCreate(BeckupSecondaryBase):
    pass

class BeckupSecondaryResponse(BeckupSecondaryBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)