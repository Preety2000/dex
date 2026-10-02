import copy
from datetime import datetime
from sqlalchemy import MetaData, desc, func, select
from sqlalchemy.orm import joinedload

from includes.core.globals.coreutils import is_empty, slugify
from includes.core.globals.entry import app_context
from includes.admin.schemas.backup import ClassBeckup
from includes.admin.modals import checked, emptyMessage
from includes.db.connection import active_secondary_db
from includes.db.dataclass import _Terms, serialize
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.cache.terms import TermsCache
from includes.db.models.secondary import (
    Article,
    ArticleMetadata,
    ArticleView,
    Suggestion,
    Terms,
    TermsRelationship,
    Trending,
    UserRelationships,
)
from includes.schemas.router_schema import DynamicURLRoute
from includes.utils.arti import get_artical_url, get_mini_article_json
from includes.utils.utils import get_post_value, get_query_value, set_response
from includes.core.query_paginator import QueryPaginator
from includes.db.models.utils import TimeStamp
from includes.metrics import MetricsManager


def getTimestamp():
    update_timestamp = TimeStamp.now_iso()
    full_timestamp = datetime.strptime(update_timestamp, "%Y-%m-%dT%H:%M:%S%z")
    return full_timestamp.date(), full_timestamp.hour, full_timestamp.minute


async def json(query: Article):
    if not query:
        return None

    def get_trending(article_id=None):
        return 0

    def rank(id):
        counts = (
            app_context.secondary_session.query(
                Trending.question.label("id"), func.count().label("cnt")
            )
            .group_by(Trending.question)
            .subquery()
        )
        ranked = app_context.secondary_session.query(
            counts.c.id,
            func.dense_rank().over(order_by=counts.c.cnt.desc()).label("rank"),
        ).subquery()
        return (
            app_context.secondary_session.query(ranked.c.rank)
            .filter(ranked.c.id == id)
            .scalar()
        )

    article = await query.to_dataclass(category=True, like=True)

    types = await TermsCache.get_by_id(article.type)
    parameters = await TermsCache.get_by_id(article.parameter)
    url = await get_artical_url(article)

    async def _json(mdata):
        if not mdata:
            return {}

        db = await active_secondary_db()

        subject = await SubjectCache.get_by_id(mdata.subject_id)
        suggestion_ints = list(map(int, filter(None, mdata.tags_group)))
        suggestion = [
            {"id": item.id, "tag": item.tags, "most_used": item.most_used}
            for item in db.query(Suggestion)
            .filter(Suggestion.id.in_(suggestion_ints))
            .all()
        ]

        dictionary = {
            "tags": suggestion,
            "subject": subject or {"name": None},
            "excerpt": mdata.excerpt,
            "secret_key": mdata.secret_key,
        }

        return dictionary

    dictionary = await _json(query.mdata)
    dictionary.update(
        {
            "rank": rank(article.id),
            "likes": article.likes,
            "types": types,
            "parameters": parameters,
            "category": article.category,
            "trending": get_trending(article.id),
            "id": query.id,
            "uri": url,
            "slug": query.slug,
            "type": query.type,
            "title": query.title,
            "views": await MetricsManager.get_article_view(article.id),
            "status": query.status,
            "content": query.content,
            "parameter": query.parameter,
            "timestamp": str(query.timestamp),
            "thumbnail": query.thumbnail,
            "comment_status": query.comment_status,
            "update_timestamp": str(query.update_timestamp),
        }
    )
    return dictionary


class ArticleService:

    @staticmethod
    async def gets(limit):

        def callback(records):
            set_response("total", records.count())
            set_response("draft", records.filter(Article.status == "Draft").count())
            set_response("publish", records.filter(Article.status == "Publish").count())

            return records

        db = await active_secondary_db()

        data = await QueryPaginator.paginate(
            limit=limit,
            types="query",
            model=Article,
            callback=callback,
            query=db.query(Article),
            transform=lambda item: json(item),
        )
        return data.records

    @staticmethod
    async def returns_error(query, error_type, data_querys):
        parameters = await TermsCache.get_by_id(query.parameter)
        record = serialize(query)
        uri = (
            parameters.slug + "/" + query.slug
            if parameters and parameters.id != 0
            else query.slug
        )
        record["uri"] = uri

        app_context.response["error"] = (
            f"This post already exists with the {error_type} : {record.get(error_type)}. Please change the slug and save. You can view the article <a target='_blank' href='/{uri}'>here</a>."
        )
        if app_context.function.is_api():
            return [{"error": app_context.response["error"], "matching": record}]
        return data_querys

    @staticmethod
    async def other_exit_data(db, article_id, data_querys):
        is_type = int(data_querys.get("type", 0))
        category = list(map(int, data_querys.get("category")))

        # Perform the bulk delete of existing TermsRelationship entries for the article_id
        db.query(Terms).filter(TermsRelationship.article_id == article_id).delete(
            synchronize_session=False
        )

        # Create and add TermsRelationship objects
        terms_relationship = [
            TermsRelationship(
                is_order=0, is_type=is_type, terms_id=terms_id, article_id=article_id
            )
            for terms_id in category
        ]
        db.add_all(terms_relationship)

        # Update and add Terms objects
        for terms_id in category:
            record = db.query(Terms).filter(Terms.id == int(terms_id)).first()
            if record:
                try:
                    record.used += 1
                except Exception:
                    record.used = 1

                TermsCache._cache(_Terms(**serialize(record)))

        is_tags = list(
            set([k.strip() for k in data_querys.get("tags").split(",") if k.strip()])
        )

        _tags = copy.deepcopy(is_tags)

        if _tags:
            # Remove existing tags and update their most_used count
            existing_tags = (
                db.query(Suggestion).filter(Suggestion.tags.in_(is_tags)).all()
            )
            for tag in existing_tags:
                tag.most_used += 1
                if tag.tags in _tags:
                    _tags.remove(tag.tags)

        # Create and add new Suggestion objects
        suggestion = [
            Suggestion(
                views=0,
                tags=tags,
                most_used=0,
                query_id=article_id,
            )
            for tags in _tags
        ]
        suggestion = db.add_all(suggestion)
        db.commit()

        suggestion = db.query(Suggestion).filter(Suggestion.tags.in_(is_tags)).all()

        # Perform the bulk delete of existing ArticleMetadata entries for the article_id
        db.query(ArticleMetadata).filter(ArticleMetadata.id == article_id).delete(
            synchronize_session=False
        )

        postsmetatags = ArticleMetadata(
            id=article_id,
            tags_group=[i.id for i in suggestion],
            subject_id=data_querys.get("subject_id"),
            excerpt=data_querys.get("excerpt"),
            secret_key=data_querys.get("secret_key"),
        )
        db.add(postsmetatags)
        db.commit()

        data_querys["tags"] = [
            {"id": item.id, "tag": item.tags, "most_used": item.most_used}
            for item in suggestion
        ]

    @staticmethod
    async def insert(data_querys):

        if app_context.response["error"]:
            return data_querys

        slug = data_querys.get("slug")
        title = data_querys.get("title")
        db = await active_secondary_db()

        db.query(Article).filter(Article.slug == slug).delete(synchronize_session=False)
        article = db.query(Article).filter(Article.slug == slug).first()
        if article:
            return await ArticleService.returns_error(article, "slug", data_querys)

        article = db.query(Article).filter(Article.title == title).first()
        if article:
            return await ArticleService.returns_error(article, "title", data_querys)

        article_query = Article(
            title=data_querys.get("title"),
            slug=data_querys.get("slug"),
            content=data_querys.get("content"),
            views=data_querys.get("views", 0),
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

        await ArticleService.other_exit_data(db, article_id, data_querys)

        # Commit the session to save changes
        db.commit()

        data_querys.update({"redirect": True})
        if app_context.function.is_api():
            article_query = json(article_query)
            return [{"insert": True, "querys": article_query}]

        return data_querys

    @staticmethod
    async def update(data_querys):
        mess = 'No articles found. You can add a new article here: <a href="/admin/content/insert">Create Article</a>'
        query_id = app_context.function.getRequestInt("item")
        if app_context.response["error"]:
            return

        if not query_id:
            app_context.response["error"] = mess
            return data_querys

        db = await active_secondary_db()
        article_query = db.query(Article).filter(Article.id == int(query_id)).first()
        if not article_query:
            app_context.response["error"] = mess
            return data_querys

        slug = data_querys.get("slug")
        title = data_querys.get("title")

        for article in db.query(Article).filter(Article.slug == slug).all():
            if not article == article_query:
                return await ArticleService.returns_error(article, "slug", data_querys)

        for article in db.query(Article).filter(Article.title == title).all():
            if not article == article_query:
                return await ArticleService.returns_error(article, "title", data_querys)

        article_query.slug = data_querys.get("slug", article_query.slug)
        article_query.title = data_querys.get("title", article_query.title)
        article_query.content = data_querys.get("content", article_query.content)
        article_query.thumbnail = data_querys.get("thumbnail", article_query.thumbnail)
        article_query.status = data_querys.get("action", article_query.status)
        article_query.parameter = data_querys.get("parameter", article_query.parameter)
        article_query.type = data_querys.get("type", article_query.type)

        article_query.comment_status = data_querys.get(
            "comment_status", article_query.comment_status
        )

        await ArticleService.other_exit_data(db, article_query.id, data_querys)
        db.commit()

        app_context.response["message"] = (
            "Update Artical <a href='/admin/content'>Back</a>"
        )
        if app_context.function.is_api():
            article_query = json(article_query)
            return [{"insert": True, "querys": article_query}]

        return data_querys

    @staticmethod
    async def get_trending_articles(limit=10):
        # Subquery to calculate trend counts

        db = await active_secondary_db()

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

        result = db.execute(query)

        records = []

        for article, rank in result.all():
            data = await get_mini_article_json(
                await article.to_dataclass(category=True, like=True),
                excerpt=True,
                trending=True,
            )

            data["rank"] = rank
            records.append(data)

        return records

    def getTimestamp(self):
        # Convert to a datetime object
        update_timestamp = TimeStamp.now_iso()

        # Assuming update_timestamp is a string like '2025-03-10 14:35:00'
        # Create a full datetime object first
        full_timestamp = datetime.strptime(update_timestamp, "%Y-%m-%dT%H:%M:%S%z")

        # Now you can update the dictionary with the correct parts
        return full_timestamp.date(), full_timestamp.hour, full_timestamp.minute

    async def get_article(query: int | Article = None):
        if isinstance(query, Article):
            return query
        db = await active_secondary_db()
        reverseds = db.query(Article)

        if isinstance(query, int):
            return reverseds.filter(Article.id == query).first()

        if isinstance(query, str):
            return reverseds.filter(Article.slug == query).first()

        return None

    @staticmethod
    async def getCollection(query: int | Article = None):

        article_query = await ArticleService.get_article(query)

        if not article_query:
            return article_query

        types = await TermsCache.get_by_id(article_query.type)
        parameters = await TermsCache.get_by_id(article_query.parameter)
        uri = (
            parameters.slug + "/" + article_query.slug
            if parameters and parameters.id != 0
            else article_query.slug
        )

        mdata = article_query.mdata
        if mdata is None:
            mdata = ArticleMetadata(
                id=article_query.id,
                tags_group=[],
                subject_id=0,
                excerpt="",
                secret_key="",
            )

        db = await active_secondary_db()

        suggestion_ints = list(map(int, filter(None, mdata.tags_group)))
        suggestion = [
            {"id": item.id, "tag": item.tags, "most_used": item.most_used}
            for item in db.query(Suggestion)
            .filter(Suggestion.id.in_(suggestion_ints))
            .all()
        ]

        dictionary = {
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
            "tags": suggestion,
        }

        dictionary.update(
            {
                "subject_id": mdata.subject_id,
                "excerpt": mdata.excerpt,
                "secret_key": mdata.secret_key,
            }
        )

        # Now you can update the dictionary with the correct parts
        date, hour, minute = getTimestamp()
        dictionary.update(
            {
                "date": date,  # Extracts the date part (YYYY-MM-DD)
                "hour": hour,  # Extracts the hour (HH)
                "minute": minute,  # Extracts the minute (MM)
            }
        )

        term_query = (
            db.query(Terms)
            .join(TermsRelationship, TermsRelationship.terms_id == Terms.id)
            .filter(TermsRelationship.article_id == article_query.id)
            .all()
        )

        dictionary.update({"category": [item.id for item in term_query]})

        return dictionary

    async def addCollection(querys):
        queryType = querys.get("type", 0)
        parameter = querys.get("parameter", 0)
        subject_id = querys.get("subject_id", 0)
        queryCategories = querys.get("category", [])

        app_context.response["subjects"] = []

        for subject in await SubjectCache.get_all():
            dictionary = {
                "id": subject.id,
                "name": subject.name,
                "slug": subject.slug,
            }
            if checked(subject.id == int(subject_id), dictionary):
                querys.update({"subject_name": subject.name})

            app_context.response["subjects"].append(dictionary)

        app_context.response["resources"] = []
        app_context.response["category"] = []

        terms = await TermsCache.get_all()

        for term in terms:
            dictionary = {
                "id": term.id,
                "name": term.name,
                "slug": term.slug,
                "subject_id": term.subject_id,
            }

            if term.topic == 1:
                category_dictionary = dictionary.copy()
                checked(
                    term.id in [int(i) for i in queryCategories], category_dictionary
                )
                if int(queryType) == term.id:
                    category_dictionary.update({"type": "checked"})

                app_context.response["category"].append(category_dictionary)

            if term.resource == 1:
                resource_dictionary = dictionary.copy()
                checked(int(parameter) == term.id, resource_dictionary)
                app_context.response["resources"].append(resource_dictionary)

        return querys

    async def action(
        id: int,
        action: str,
    ):

        db = await active_secondary_db()
        article = db.query(Article).filter(Article.id == int(id)).first()
        if article and action in ["trash", "publish"]:
            article.status = "Draft" if action == "trash" else "Publish"
            db.commit()
            return True

        if article and action == "delete":
            data_querys = await ArticleService.getCollection(article)
            if await ClassBeckup.insert(data_querys, "article"):
                db.query(ArticleMetadata).filter_by(id=article.id).delete()
                db.query(UserRelationships).filter_by(article_id=article.id).delete()
                db.query(Terms).filter_by(article_id=article.id).delete()
                db.query(Article).filter_by(id=article.id).delete()
                db.commit()

                return True

            app_context.response["pop_message"] = {
                "title": "This 'article' could not be deleted. Error code: Ae8349",
                "url": "/admin/content",
            }
            return None

        app_context.response["pop_message"] = {
            "title": "This 'article' could not be deleted. Error code: Ae8340",
            "url": "/admin/content",
        }
        return None

    @staticmethod
    async def index(roots: DynamicURLRoute):
        item = app_context.function.getRequestInt("item")
        action = get_query_value("action")

        if item and action:
            if await ArticleService.action(item, action):
                MetaData.redirect_url = "/admin/content"
                return "redirect"

        if roots.scope_slug not in ("insert", "update"):
            app_context.response["data_querys"] = await ArticleService.gets(10)
            return "admin/articles"

        date, hour, minute = getTimestamp()
        DEFAULT_FIELDS = {
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

        OPTIONAL_FIELDS = {
            "trackback_url",
            "thumbnail",
            "category[]",
            "tags",
            "secret_key",
            "metavalue",
        }

        INTEGER_FIELDS = {"type", "subject_id", "parameter"}

        # is_response[TimeStamp.now_iso()] = "555"

        article_data = None
        if item and not app_context.function.is_post():
            article_data = await ArticleService.getCollection(int(item))

        if app_context.function.is_post():
            keys_list = list(DEFAULT_FIELDS.keys())
            defaults_list = list(DEFAULT_FIELDS.values())

            article_data = await get_post_value(keys_list, defaults_list)
            option_slug = (
                article_data.get("title")
                if is_empty(article_data.get("slug"))
                else article_data.get("slug")
            )
            article_data["slug"] = slugify(option_slug)

            for field in INTEGER_FIELDS:
                article_data[field] = int(article_data.get(field) or 0)

            for key, value in article_data.items():
                if is_empty(value) and key not in OPTIONAL_FIELDS:
                    current_error = app_context.response.get("error")
                    app_context.response["error"] = current_error or emptyMessage(
                        key, roots.scope_slug
                    )

        elif not article_data:
            article_data = {
                key.replace("[]", ""): val for key, val in DEFAULT_FIELDS.items()
            }

        update_timestamp = TimeStamp.now_iso()
        date_object = datetime.strptime(update_timestamp, "%Y-%m-%dT%H:%M:%S%z")

        if "category[]" in article_data:
            article_data["category"] = article_data.pop("category[]")

        article_data["update_timestamp"] = date_object
        if app_context.function.is_post():
            bind_function = getattr(ArticleService, roots.scope_slug, None)

            if callable(bind_function):
                bind_value = await bind_function(article_data)

                if bind_value:
                    if isinstance(bind_value, dict):
                        if bind_value.get("redirect"):
                            MetaData.redirect_url = "/admin/content"
                            return "redirect"
                        app_context.response["data_querys"] = bind_value

                    elif isinstance(bind_value, list):
                        return bind_value

        app_context.response["data_querys"] = await ArticleService.addCollection(
            article_data
        )
        return "admin/add_articles"
