import json
from sqlalchemy.ext.declarative import declarative_base
from includes.core.globals.entry import app_context
from includes.core.globals.coreutils import format_view_count
from includes.core.globals.coreutils import format_TimeStamp
from includes.db.models.utils import TimeStamp, JsonList
from sqlalchemy.orm import column_property, relationship
from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    String,
    Text,
    TypeDecorator,
    func,
    select,
)
from includes.db.dataclass import (
    _Article,
    _PostsMetaTags,
    _Suggestion,
    _Terms,
    serialize,
)


class MCQJsonList(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        try:
            return json.loads(value)
        except:
            try:
                if isinstance(value, str):
                    return value.split("#HAS")
            except:
                return []


BaseSecondary = declarative_base()


class Writers(BaseSecondary):
    __tablename__ = "writers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    excerpt = Column(Text)
    slug = Column(Text, nullable=True)


class Books(BaseSecondary):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    excerpt = Column(Text)
    writer = Column(Integer)
    subject = Column(Integer)
    image_src = Column(Text)
    slug = Column(Text, nullable=True)


class University(BaseSecondary):
    __tablename__ = "university"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    used = Column(Integer, nullable=False)


class Syllabus(BaseSecondary):
    __tablename__ = "syllabus"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    university = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)


class Courses(BaseSecondary):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    university = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)


class Jobs(BaseSecondary):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    types = Column(Integer, nullable=False)
    admitcard = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    lastsate = Column(TimeStamp, nullable=False)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)


class BooksRelationship(BaseSecondary):
    __tablename__ = "books_relationships"
    books_id = Column(Integer, primary_key=True)
    terms_id = Column(Integer, primary_key=True)


class QuizRelationships(BaseSecondary):
    __tablename__ = "quiz_relationships"
    terms_id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, primary_key=True)


class TermsRelationship(BaseSecondary):
    __tablename__ = "terms_relationship"
    is_type = Column(Integer)
    is_order = Column(Integer, nullable=False)
    article_id = Column(Integer, primary_key=True)
    terms_id = Column(Integer, primary_key=True)


class UserRelationships(BaseSecondary):
    __tablename__ = "users_relationships"
    article_id = Column(Integer, primary_key=True)
    users_id = Column(Integer, primary_key=True)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)


class QuizQuestion(BaseSecondary):
    __tablename__ = "quiz_question"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    incorrect_answers = Column(MCQJsonList, default=list)
    subject_id = Column(Integer, nullable=False)
    status = Column(String(100), nullable=False)
    views = Column(Integer, nullable=False)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    def next_prev_question(self):
        # Base query for QuizQuestion
        terms = None
        base = app_context.db.query(QuizQuestion)

        # Agar Category filtering lagi ho (e.g. /practice/category/jharkhand-gk)
        if app_context.route.scope_slug != "tagged" and app_context.route.resource_type:
            base = (
                base.join(
                    QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id
                )
                .join(Terms, Terms.id == QuizRelationships.terms_id)
                .filter(Terms.slug == app_context.route.scope_slug)
            )
            terms = (
                app_context.db.query(Terms)
                .filter(Terms.slug == app_context.route.scope_slug)
                .first()
            )

        # Previous Question: ID chota ho aur descending order me pehla item
        self.prev = (
            base.filter(QuizQuestion.id < self.id)
            .order_by(QuizQuestion.id.desc())
            .first()
        )

        # Next Question: ID bada ho aur ascending order me pehla item
        self.next = (
            base.filter(QuizQuestion.id > self.id)
            .order_by(QuizQuestion.id.asc())
            .first()
        )

        if self.prev:
            self.prev.terms = terms

        if self.next:
            self.next.terms = terms

        return self

    def to_dict(self):
        data = serialize(self)

        term_query = (
            app_context.db.query(Terms)
            .join(QuizRelationships, QuizRelationships.terms_id == Terms.id)
            .filter(QuizRelationships.quiz_id == self.id)
        )

        data["url"] = (
            f"{app_context.request.host_url}practice{f"/{self.terms.slug}" if hasattr(self, "terms") else ""}/{self.id}"
        )
        data["category"] = [
            {
                "id": term.id,
                "url": f"/practice/tagged/{term.slug}",
                "img": term.img,
                "used": term.used,
                "name": term.name,
                "mcq_count": term.mcq_count,
                "description": term.description,
            }
            for term in term_query.all()
        ]

        return data


class Article(BaseSecondary):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    parameter = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)
    update_timestamp = Column(
        TimeStamp, default=TimeStamp.now_iso, onupdate=TimeStamp.now_iso
    )
    thumbnail = Column(Text, nullable=True)
    status = Column(String(255), nullable=True)
    comment_status = Column(String(100), nullable=True)
    type = Column(Integer, nullable=False)

    mdata = relationship(
        "ArticleMetadata",
        primaryjoin="Article.id == foreign(ArticleMetadata.id)",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @staticmethod
    async def add_prev_next_article(article: _Article) -> _Article:

        # Previous and next article navigation
        if not isinstance(article.parameter, int):
            raise TabError("Article parameter not be int")

        param_articles = app_context.db.query(Article).filter(
            Article.parameter == article.parameter
        )

        prev_article = (
            param_articles.filter(Article.id < article.id)
            .order_by(Article.id.desc())
            .first()
        )
        next_article = (
            param_articles.filter(Article.id > article.id)
            .order_by(Article.id.asc())
            .first()
        )

        article.prev_article = (
            _Article(**serialize(prev_article)) if prev_article else None
        )
        article.next_article = (
            _Article(**serialize(next_article)) if next_article else None
        )

        return article

    async def to_dataclass(self, *, category=None, like=None) -> _Article:
        article = _Article(**serialize(self))
        article.date = format_TimeStamp(self.timestamp)

        if like is True:
            article.likes = (
                app_context.db.query(UserRelationships)
                .filter(UserRelationships.article_id == self.id)
                .count()
            )

        if category is True:
            term_query = (
                app_context.db.query(Terms)
                .join(TermsRelationship, TermsRelationship.terms_id == Terms.id)
                .filter(TermsRelationship.article_id == self.id)
            )
            article.category = [_Terms(**serialize(term)) for term in term_query.all()]

        return article


class Terms(BaseSecondary):
    __tablename__ = "terms"
    id = Column(Integer, primary_key=True)
    slug = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    image_src = Column(Text, default="empty.png")
    resource = Column(Integer, nullable=False)
    topic = Column(Integer, nullable=False)
    subject_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    used = Column(Integer, default=0)

    @property
    def img(self):
        return (
            self.image_src
            if "/" in self.image_src
            else f"/media/img/category/{self.image_src}"
        )

    @property
    def url(self):
        return f"{app_context.request.host_url}questions/tagged/{self.slug}"

    mcq_count = column_property(
        select(func.count(QuizRelationships.quiz_id))
        .where(QuizRelationships.terms_id == id)
        .correlate_except(QuizRelationships)
        .scalar_subquery()
    )
    article_count = column_property(
        select(func.count(TermsRelationship.article_id))
        .where(TermsRelationship.terms_id == id)
        .correlate_except(TermsRelationship)
        .scalar_subquery()
    )


class ArticleMetadata(BaseSecondary):
    __tablename__ = "article_meta_tags"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    subject_id = Column(Integer, nullable=True)
    excerpt = Column(Text, nullable=False)
    tags_group = Column(JsonList, default=list)
    secret_key = Column(Text, nullable=True)

    def dataclass(self) -> _PostsMetaTags:
        return _PostsMetaTags(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )


class Suggestion(BaseSecondary):
    __tablename__ = "suggestion"
    views = Column(Integer, nullable=False)
    query_id = Column(Integer, nullable=False)
    tags = Column(String(255), nullable=False, unique=True)
    most_used = Column(Integer, nullable=False, default=0)
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    def to_dataclass(self) -> _Suggestion:
        return _Suggestion(
            **{field: getattr(self, field) for field in self.__table__.columns.keys()}
        )


class Trending(BaseSecondary):
    __tablename__ = "trending"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Integer)
    trending = Column(Integer)
    # question = Column(Integer, primary_key=True)
    # trending = Column(Integer, primary_key=True)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)


class Beckup(BaseSecondary):
    __tablename__ = "backup"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    types = Column(String(100), nullable=False)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)


class ArticleView(BaseSecondary):
    __tablename__ = "article_views"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(100), nullable=True, index=True)

    view_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TimeStamp, nullable=False, default=TimeStamp.now_iso)
    updated_at = Column(
        TimeStamp,
        nullable=False,
        default=TimeStamp.now_iso,
        onupdate=TimeStamp.now_iso,
    )


class QuizView(BaseSecondary):
    __tablename__ = "quiz_views"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(100), nullable=True, index=True)

    view_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TimeStamp, nullable=False, default=TimeStamp.now_iso)
    updated_at = Column(
        TimeStamp,
        nullable=False,
        default=TimeStamp.now_iso,
        onupdate=TimeStamp.now_iso,
    )


def bindBaseSecondaryModelsToSession(session):
    session.jobs = session.query(Jobs)
    session.terms = session.query(Terms)
    session.books = session.query(Books)
    session.backup = session.query(Beckup)
    session.article = session.query(Article)
    session.writers = session.query(Writers)
    session.courses = session.query(Courses)
    session.syllabus = session.query(Syllabus)
    session.trending = session.query(Trending)
    session.suggestion = session.query(Suggestion)
    session.university = session.query(University)
    session.quizquestion = session.query(QuizQuestion)
    session.postsmetatags = session.query(ArticleMetadata)
    session.quizrelationships = session.query(QuizRelationships)
    session.termsrelationship = session.query(TermsRelationship)
    session.booksrelationship = session.query(BooksRelationship)
    session.userrelationships = session.query(UserRelationships)
    return session
