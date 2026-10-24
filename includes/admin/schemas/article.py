import copy
from datetime import datetime
from typing import Any, List, Optional, Tuple, Union

from includes.src.request import Request
from sqlalchemy import case, delete, desc, func, select, text, update

from includes.admin.modals import checked, emptyMessage
from includes.admin.schemas.backup import ClassBeckup
from includes.core.globals.coreutils import is_empty, slugify
from includes.core.globals.entry import app_context

from includes.core.globals.route_context import Route

from includes.core.paginator import NewQueryPaginator
from includes.database.connection import config_secondary_db
from includes.database.dataclass.dataclass import _Terms, serialize
from includes.database.models.secondary import (
    Article,
    ArticleMetadata,
    ArticleView,
    Suggestion,
    Terms,
    TermsRelationship,
    Trending,
    UserRelationships,
)
from includes.database.models.utils import TimeStamp
from includes.metrics import MetricsManager
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.cache.terms import TermsCache
from includes.utils.arti import get_artical_url, get_mini_article_json
from includes.utils.utils import get_post_value, set_response


def get_timestamp() -> Tuple[Any, int, int]:
    """Helper to retrieve current ISO date, hour, and minute."""
    update_timestamp = TimeStamp.now_iso()
    try:
        full_timestamp = datetime.fromisoformat(update_timestamp)
    except ValueError:
        full_timestamp = datetime.strptime(update_timestamp, "%Y-%m-%dT%H:%M:%S%z")
    return full_timestamp.date(), full_timestamp.hour, full_timestamp.minute


async def json(query: Article) -> Optional[dict[str, Any]]:
    """Serialize Article model into a JSON-compatible dictionary."""
    if not query:
        return None

    def get_trending(article_id: int = None) -> int:
        return 0

    def rank(article_id: int) -> Optional[int]:
        session = app_context.secondary_session
        counts_stmt = (
            select(Trending.question.label("id"), func.count().label("cnt"))
            .group_by(Trending.question)
            .subquery()
        )
        ranked_stmt = select(
            counts_stmt.c.id,
            func.dense_rank().over(order_by=counts_stmt.c.cnt.desc()).label("rank"),
        ).subquery()

        stmt = select(ranked_stmt.c.rank).where(ranked_stmt.c.id == article_id)
        return session.execute(stmt).scalar()

    article = await query.to_dataclass(category=True, like=True)

    types = await TermsCache.get_by_id(article.type)
    parameters = await TermsCache.get_by_id(article.parameter)
    url = await get_artical_url(article)

    async def _fetch_metadata(mdata: Optional[ArticleMetadata]) -> dict[str, Any]:
        if not mdata:
            return {}

        db = await config_secondary_db()
        subject = await SubjectCache.get_by_id(mdata.subject_id)
        suggestion_ints = list(map(int, filter(None, mdata.tags_group or [])))

        stmt = select(Suggestion).where(Suggestion.id.in_(suggestion_ints))
        suggestions = db.execute(stmt).scalars().all()

        return {
            "tags": [
                {"id": item.id, "tag": item.tags, "most_used": item.most_used}
                for item in suggestions
            ],
            "subject": subject or {"name": None},
            "excerpt": mdata.excerpt,
            "secret_key": mdata.secret_key,
        }

    metadata_dict = await _fetch_metadata(article.mdata)
    # views_count = await MetricsManager.get_article_view(article.id)

    metadata_dict.update(
        {
            "id": query.id,
            "rank": rank(article.id),
            "types": types,
            "parameters": parameters,
            "category": article.category,
            "trending": get_trending(article.id),
            "uri": url,
            "slug": query.slug,
            "type": query.type,
            "title": query.title,
            "status": query.status,
            "content": query.content,
            "parameter": query.parameter,
            "timestamp": str(query.timestamp),
            "thumbnail": query.thumbnail,
            "comment_status": query.comment_status,
            "update_timestamp": str(query.update_timestamp),
        }
    )

    return metadata_dict


class AdminArticleService:

    def __init__(self, request):
        self.request = request

    @staticmethod
    def get_timestamp() -> Tuple[Any, int, int]:
        return get_timestamp()

    async def gets(self, limit: int) -> List[dict[str, Any]]:
        db = await config_secondary_db()
        stmt = select(
            func.count(Article.id).label("total"),
            func.count(case((Article.status == "Draft", 1))).label("draft"),
            func.count(case((Article.status == "Publish", 1))).label("publish"),
        )

        # Single query execution
        result = db.execute(stmt).one()

        # Response set karein
        set_response(self.request, "total", result.total)
        set_response(self.request, "draft", result.draft)
        set_response(self.request, "publish", result.publish)

        data = await NewQueryPaginator.paginate(
            db=db,
            limit=limit,
            request=self.request,
            types="query",
            model=Article,
            query=select(Article),
            transform=lambda item: json(item),
            desc="id",
        )

        return data.records

    async def returns_error(
        self, query: Article, error_type: str, data_querys: dict[str, Any]
    ):
        parameters = await TermsCache.get_by_id(query.parameter)
        record = serialize(query)
        uri = (
            f"{parameters.slug}/{query.slug}"
            if parameters and parameters.id != 0
            else query.slug
        )
        record["uri"] = uri

        error_msg = (
            f"This post already exists with the {error_type} : {record.get(error_type)}. "
            f"Please change the slug and save. You can view the article "
            f"<a target='_blank' href='/{uri}'>here</a>."
        )
        self.request.state.response["error"] = error_msg

        if self.request.method == "POST" and self.request.query_params.get("key"):
            return [{"error": error_msg, "matching": record}]
        return data_querys

    @staticmethod
    async def other_exit_data(db, article_id: int, data_querys: dict[str, Any]):
        is_type = int(data_querys.get("type", 0))
        categories = [int(c) for c in data_querys.get("category", [])]

        # Bulk delete existing TermsRelationship for this article
        db.execute(
            delete(TermsRelationship).where(TermsRelationship.article_id == article_id)
        )
        db.flush()
        # Add new TermsRelationships
        terms_relationships = [
            TermsRelationship(
                is_order=0, is_type=is_type, terms_id=terms_id, article_id=article_id
            )
            for terms_id in categories
        ]
        db.add_all(terms_relationships)
        db.flush()
        # Update Terms usage counter & cache
        for terms_id in categories:
            stmt = select(Terms).where(Terms.id == terms_id)
            record = db.execute(stmt).scalar_one_or_none()
            if record:
                record.used = (record.used or 0) + 1
                TermsCache._cache(_Terms(**serialize(record)))

        # Parse & sync tags/suggestions
        raw_tags = data_querys.get("tags", "")
        if isinstance(raw_tags, str):
            tag_list = list({k.strip() for k in raw_tags.split(",") if k.strip()})
        else:
            tag_list = list(set(raw_tags or []))

        remaining_tags = copy.deepcopy(tag_list)

        # db.execute(text("DROP TABLE IF EXISTS suggestion"))
        # db.commit()

        if remaining_tags:
            stmt = select(Suggestion).where(Suggestion.tags.in_(tag_list))
            existing_tags = db.execute(stmt).scalars().all()
            for tag in existing_tags:
                tag.most_used += 1
                if tag.tags in remaining_tags:
                    remaining_tags.remove(tag.tags)

        new_suggestions = [
            Suggestion(views=0, tags=tag, most_used=0, query_id=article_id)
            for tag in remaining_tags
        ]
        db.add_all(new_suggestions)
        db.commit()

        # Re-fetch all active tags for this article
        stmt = select(Suggestion).where(Suggestion.tags.in_(tag_list))
        all_suggestions = db.execute(stmt).scalars().all()

        # 5. Delete & insert ArticleMetadata
        db.execute(delete(ArticleMetadata).where(ArticleMetadata.id == article_id))

        db.flush()
        postsmetatags = ArticleMetadata(
            id=article_id,
            tags_group=[item.id for item in all_suggestions],
            subject_id=data_querys.get("subject_id"),
            excerpt=data_querys.get("excerpt"),
            secret_key=data_querys.get("secret_key"),
        )
        db.add(postsmetatags)
        db.commit()

        data_querys["tags"] = [
            {"id": item.id, "tag": item.tags, "most_used": item.most_used}
            for item in all_suggestions
        ]

    async def insert(self, data_querys: dict[str, Any]):
        if self.request.state.response.get("error"):
            return data_querys

        slug = data_querys.get("slug")
        title = data_querys.get("title")
        db = await config_secondary_db()

        # Check slug collision
        stmt_slug = select(Article).where(Article.slug == slug)
        existing_slug = db.execute(stmt_slug).scalar_one_or_none()
        if existing_slug:
            return await self.returns_error(existing_slug, "slug", data_querys)

        # Check title collision
        stmt_title = select(Article).where(Article.title == title)
        existing_title = db.execute(stmt_title).scalar_one_or_none()
        if existing_title:
            return await self.returns_error(existing_title, "title", data_querys)

        article_query = Article(
            title=title,
            slug=slug,
            content=data_querys.get("content"),
            parameter=data_querys.get("parameter"),
            timestamp=data_querys.get("timestamp"),
            thumbnail=data_querys.get("thumbnail"),
            status=data_querys.get("action"),
            type=data_querys.get("type"),
            comment_status=data_querys.get("comment_status"),
            update_timestamp=data_querys.get("update_timestamp"),
        )
        db.add(article_query)
        db.commit()
        db.refresh(article_query)

        article_id = int(article_query.id)
        await AdminArticleService.other_exit_data(db, article_id, data_querys)
        db.commit()

        data_querys.update({"redirect": True})
        if self.request.method == "POST" and self.request.query_params.get("key"):
            article_serialized = await json(article_query)
            return [{"insert": True, "querys": article_serialized}]

        return data_querys

    async def update(self, data_querys: dict[str, Any]):
        error_msg = (
            "No articles found. You can add a new article here: "
            '<a href="/admin/content/insert">Create Article</a>'
        )
        query_id = self.request.query_params.get("item")

        if self.request.state.response.get("error"):
            return

        if not query_id:
            self.request.state.response["error"] = error_msg
            return data_querys

        db = await config_secondary_db()

        stmt = select(Article).where(Article.id == int(query_id))
        article_query = db.execute(stmt).scalar_one_or_none()
        if not article_query:
            self.request.state.response["error"] = error_msg
            return data_querys

        slug = data_querys.get("slug")
        title = data_querys.get("title")

        # Check slug duplicate excluding current article
        stmt_slug = select(Article).where(
            Article.slug == slug, Article.id != article_query.id
        )
        slug_collision = db.execute(stmt_slug).scalars().first()
        if slug_collision:
            return await self.returns_error(slug_collision, "slug", data_querys)

        # Check title duplicate excluding current article
        stmt_title = select(Article).where(
            Article.title == title, Article.id != article_query.id
        )
        title_collision = db.execute(stmt_title).scalars().first()
        if title_collision:
            return await self.returns_error(title_collision, "title", data_querys)

        # Update article fields
        article_query.slug = slug or article_query.slug
        article_query.title = title or article_query.title
        article_query.content = data_querys.get("content", article_query.content)
        article_query.thumbnail = data_querys.get("thumbnail", article_query.thumbnail)
        article_query.status = data_querys.get("action", article_query.status)
        article_query.parameter = data_querys.get("parameter", article_query.parameter)
        article_query.type = data_querys.get("type", article_query.type)
        article_query.comment_status = data_querys.get(
            "comment_status", article_query.comment_status
        )

        await AdminArticleService.other_exit_data(db, article_query.id, data_querys)
        db.commit()

        self.request.state.response["message"] = (
            "Update Article <a href='/admin/content'>Back</a>"
        )

        if self.request.method == "POST" and self.request.query_params.get("key"):
            article_serialized = await json(article_query)
            return [{"insert": True, "querys": article_serialized}]

        return data_querys

    @staticmethod
    async def get_trending_articles(limit: int = 10) -> List[dict[str, Any]]:
        db = await config_secondary_db()

        rank_column = (
            func.row_number()
            .over(
                order_by=(ArticleView.updated_at.desc(), ArticleView.view_count.desc())
            )
            .label("rank")
        )

        query = (
            select(Article, rank_column)
            .join(ArticleView, Article.id == ArticleView.id)
            .where(Article.status == "Publish", Article.parameter != 0)
            .order_by(ArticleView.updated_at.desc(), ArticleView.view_count.desc())
            .limit(limit)
        )

        result = db.execute(query).all()
        records = []

        for article, rank in result:
            data = await get_mini_article_json(
                await article.to_dataclass(category=True, like=True),
                excerpt=True,
                trending=True,
            )
            data["rank"] = rank
            records.append(data)

        return records

    @staticmethod
    async def get_article(query: Union[int, str, Article] = None) -> Optional[Article]:
        if isinstance(query, Article):
            return query

        if not query:
            return None

        db = await config_secondary_db()

        if isinstance(query, int):
            stmt = select(Article).where(Article.id == query)
        elif isinstance(query, str):
            stmt = select(Article).where(Article.slug == query)
        else:
            return None

        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    async def getCollection(
        query: Union[int, str, Article] = None,
    ) -> Optional[dict[str, Any]]:
        article_query = await AdminArticleService.get_article(query)
        if not article_query:
            return None

        parameters = await TermsCache.get_by_id(article_query.parameter)
        uri = (
            f"{parameters.slug}/{article_query.slug}"
            if parameters and parameters.id != 0
            else article_query.slug
        )

        db = await config_secondary_db()
        metadata_stmt = select(ArticleMetadata).where(
            ArticleMetadata.id == article_query.id
        )
        mdata = db.execute(metadata_stmt).scalars().first()
        if mdata is None:
            mdata = ArticleMetadata(
                id=article_query.id,
                tags_group=[],
                subject_id=0,
                excerpt="",
                secret_key="",
            )

        suggestion_ints = list(map(int, filter(None, mdata.tags_group or [])))
        stmt = select(Suggestion).where(Suggestion.id.in_(suggestion_ints))
        suggestions = db.execute(stmt).scalars().all()

        date, hour, minute = get_timestamp()

        # Terms / Categories lookup
        term_stmt = (
            select(Terms)
            .join(TermsRelationship, TermsRelationship.terms_id == Terms.id)
            .where(TermsRelationship.article_id == article_query.id)
        )
        term_query = db.execute(term_stmt).scalars().all()

        return {
            "id": article_query.id,
            "uri": uri,
            "type": article_query.type,
            "slug": article_query.slug,
            "title": article_query.title,
            "status": article_query.status,
            "content": article_query.content,
            "parameter": article_query.parameter,
            "timestamp": article_query.timestamp,
            "thumbnail": article_query.thumbnail,
            "comment_status": article_query.comment_status,
            "update_timestamp": article_query.update_timestamp,
            "tags": [
                {"id": item.id, "tag": item.tags, "most_used": item.most_used}
                for item in suggestions
            ],
            "subject_id": mdata.subject_id,
            "excerpt": mdata.excerpt,
            "secret_key": mdata.secret_key,
            "date": date,
            "hour": hour,
            "minute": minute,
            "category": [item.id for item in term_query],
        }

    async def addCollection(self, querys: dict[str, Any]) -> dict[str, Any]:
        query_type = querys.get("type", 0)
        parameter = querys.get("parameter", 0)
        subject_id = querys.get("subject_id", 0)
        query_categories = [int(i) for i in querys.get("category", [])]

        self.request.state.response["subjects"] = []
        for subject in await SubjectCache.get_all():
            dictionary = {
                "id": subject.id,
                "name": subject.name,
                "slug": subject.slug,
            }
            if checked(subject.id == int(subject_id), dictionary):
                querys["subject_name"] = subject.name

            self.request.state.response["subjects"].append(dictionary)

        self.request.state.response["resources"] = []
        self.request.state.response["category"] = []

        terms = await TermsCache.get_all()
        for term in terms:
            dictionary = {
                "id": term.id,
                "name": term.name,
                "slug": term.slug,
                "subject_id": term.subject_id,
            }

            if term.topic == 1:
                category_dict = dictionary.copy()
                checked(term.id in query_categories, category_dict)
                if int(query_type) == term.id:
                    category_dict["type"] = "checked"
                self.request.state.response["category"].append(category_dict)

            if term.resource == 1:
                resource_dict = dictionary.copy()
                checked(int(parameter) == term.id, resource_dict)
                self.request.state.response["resources"].append(resource_dict)

        return querys

    async def action(self, id: int, action_type: str) -> Optional[bool]:
        db = await config_secondary_db()

        stmt = select(Article).where(Article.id == int(id))
        article = db.execute(stmt).scalar_one_or_none()

        if article and action_type in ["trash", "publish"]:
            article.status = "Draft" if action_type == "trash" else "Publish"
            db.commit()
            return True

        if article and action_type == "delete":
            data_querys = await AdminArticleService.getCollection(article)
            backup_status = None
            if not self.request.state.response["error"]:
                backup_status = await ClassBeckup.insert(data_querys, "article")

            if backup_status:
                db.execute(
                    delete(ArticleMetadata).where(ArticleMetadata.id == article.id)
                )
                db.execute(
                    delete(UserRelationships).where(
                        UserRelationships.article_id == article.id
                    )
                )
                db.execute(
                    delete(TermsRelationship).where(
                        TermsRelationship.article_id == article.id
                    )
                )
                db.execute(delete(Article).where(Article.id == article.id))
                db.commit()
                return True

            self.request.state.response["pop_message"] = {
                "title": "This 'article' could not be deleted. Error code: Ae8349",
                "url": "/admin/content",
            }
            return None

        self.request.state.response["pop_message"] = {
            "title": "This 'article' could not be deleted. Error code: Ae8340",
            "url": "/admin/content",
        }
        return None

    async def index(self, roots: Route):
        item = self.request.query_params.get("item")
        action = self.request.query_params.get("action")

        if item and action:
            if await self.action(item, action):
                self.request.state.metadata.redirect_url = "/admin/content"
                return "redirect"

        if roots.scope not in ("insert", "update"):
            self.request.state.response["data_querys"] = await self.gets(10)
            return "admin/articles"

        date, hour, minute = get_timestamp()

        default_fields = {
            "title": "",
            "action": "",
            "subject_id": 0,
            "date": date,
            "hour": hour,
            "minute": minute,
            "advanced_view": 0,
            "comment_status": "",
            "trackback_url": "",
            "thumbnail": "",
            "category[]": [],
            "type": 0,
            "parameter": 0,
            "slug": "",
            "secret_key": "",
            "content": "",
            "excerpt": "",
            "tags": "",
            "metavalue": "",
        }

        optional_fields = {
            "trackback_url",
            "thumbnail",
            "category[]",
            "tags",
            "secret_key",
            "metavalue",
        }

        integer_fields = {"type", "subject_id", "parameter"}

        article_data = None
        if item and not self.request.is_post:
            article_data = await self.getCollection(int(item))

        if self.request.is_post:
            keys_list = list(default_fields.keys())
            defaults_list = list(default_fields.values())

            article_data = await get_post_value(self.request, keys_list, defaults_list)
            option_slug = (
                article_data.get("title")
                if is_empty(article_data.get("slug"))
                else article_data.get("slug")
            )
            article_data["slug"] = slugify(option_slug)

            for field in integer_fields:
                article_data[field] = int(article_data.get(field) or 0)

            for key, value in article_data.items():
                if is_empty(value) and key not in optional_fields:
                    current_error = self.request.state.response.get("error")
                    self.request.state.response["error"] = (
                        current_error or emptyMessage(key, roots.scope)
                    )

        elif not article_data:
            article_data = {
                key.replace("[]", ""): val for key, val in default_fields.items()
            }

        update_timestamp = TimeStamp.now_iso()
        try:
            date_object = datetime.fromisoformat(update_timestamp)
        except ValueError:
            date_object = datetime.strptime(update_timestamp, "%Y-%m-%dT%H:%M:%S%z")

        if "category[]" in article_data:
            article_data["category"] = article_data.pop("category[]")

        article_data["update_timestamp"] = date_object

        if self.request.is_post:
            bind_function = getattr(self, roots.scope, None)

            if callable(bind_function):
                bind_value = await bind_function(article_data)

                if bind_value:
                    if isinstance(bind_value, dict):
                        if bind_value.get("redirect"):
                            self.request.state.metadata.redirect_url = "/admin/content"
                            return "redirect"
                        self.request.state.response["data_querys"] = bind_value

                    elif isinstance(bind_value, list):
                        return bind_value

        self.request.state.response["data_querys"] = await self.addCollection(
            article_data
        )
        return "admin/add_articles"
