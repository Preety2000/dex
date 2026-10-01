import inspect
from typing import Optional
from bs4 import BeautifulSoup
from sqlalchemy import desc, func, select
from includes.core.config import app_context
from includes.db.connection import active_secondary_db
from includes.core.new_query_paginator import NewQueryPaginator
from includes.core.query_paginator import QueryPaginator
from includes.db.dataclass import _Article, _Terms, serialize, to_dict
from includes.db.models.secondary import (
    Article,
    TermsRelationship,
    Trending,
    UserRelationships,
)
from includes.schemas.cache.likes import Likes
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.cache.suggestion import SuggestionCache
from includes.schemas.cache.terms import TermsCache
from includes.metrics import MetricsManager
from includes.utils.arti import enrich_article, get_artical_url, get_mini_article_json

articalNotFondmessage = "<h2>Error: Can't read file, or Article cannot be opened</h2><p>It looks like you’re dealing with an error message indicating that a file can't be read or an article cannot be opened. Here are a few potential reasons for this issue and ways to troubleshoot:</p><ol><li><p><strong>File Path Issues</strong>:</p><ul><li><strong>Check File Path</strong>: Ensure that the file path you’re using is correct. Verify that the file exists at the specified location.</li><li><strong>Relative vs. Absolute Paths</strong>: If you’re using a relative path, try using an absolute path to avoid ambiguity.</li></ul></li><li><p><strong>File Permissions</strong>:</p><ul><li><strong>Permissions</strong>: Ensure that you have the necessary permissions to access the file. You might need to adjust the file permissions or run your application with higher privileges.</li></ul></li><li><p><strong>File Corruption</strong>:</p><ul><li><strong>Check File Integrity</strong>: The file might be corrupted or damaged. Try opening it with a different application or tool to see if it works.</li></ul></li><li><p><strong>File Format</strong>:</p><ul><li><strong>Supported Formats</strong>: Verify that the file format is supported by your application. If not, you might need to convert the file to a compatible format.</li></ul></li><li><p><strong>Application Errors</strong>:</p><ul><li><strong>Error Handling</strong>: Make sure that your application has proper error handling to deal with file-related issues gracefully.</li><li><strong>Logs and Debugging</strong>: Check application logs or debug output for more specific error messages.</li></ul></li></ol>"
articalNotFondmessage = "<h2>त्रुटि: फ़ाइल नहीं पढ़ी जा सकती, या लेख नहीं खोला जा सकता</h2><p>ऐसा लगता है कि आप एक त्रुटि संदेश से निपट रहे हैं जो यह दर्शाता है कि फ़ाइल पढ़ी नहीं जा सकती या लेख नहीं खोला जा सकता। इस समस्या के कुछ संभावित कारण और समस्या निवारण के तरीके यहां दिए गए हैं:</p><ol><li><p><strong>फ़ाइल पथ समस्याएँ</strong>:</p><ul><li><strong>फ़ाइल पथ जाँचें</strong>: सुनिश्चित करें कि आप जिस फ़ाइल पथ का उपयोग कर रहे हैं वह सही है। सत्यापित करें कि फ़ाइल निर्दिष्ट स्थान पर मौजूद है।</li><li><strong>सापेक्ष बनाम निरपेक्ष पथ</strong>: यदि आप सापेक्ष पथ का उपयोग कर रहे हैं, तो अस्पष्टता से बचने के लिए निरपेक्ष पथ का उपयोग करने का प्रयास करें।</li></ul></li><li><p><strong>फ़ाइल अनुमतियाँ</strong>:</p><ul><li><strong>अनुमतिएँ</strong>: सुनिश्चित करें कि आपके पास फ़ाइल तक पहुँचने के लिए आवश्यक अनुमतियाँ हैं। आपको फ़ाइल अनुमतियों को समायोजित करने या अपने एप्लिकेशन को उच्च विशेषाधिकारों के साथ चलाने की आवश्यकता हो सकती है।</li></ul></li><li><p><strong>फ़ाइल भ्रष्टाचार</strong>:</p><ul><li><strong>फ़ाइल अखंडता की जाँच करें</strong>: फ़ाइल दूषित या क्षतिग्रस्त हो सकती है। यह देखने के लिए कि क्या यह काम करता है, इसे किसी अन्य एप्लिकेशन या टूल के साथ खोलने का प्रयास करें।</li></ul></li><li><p><strong>फ़ाइल प्रारूप</strong>:</p><ul><li><strong>समर्थित प्रारूप</strong>: सत्यापित करें कि फ़ाइल प्रारूप आपके एप्लिकेशन द्वारा समर्थित है। यदि नहीं, तो आपको फ़ाइल को संगत प्रारूप में परिवर्तित करने की आवश्यकता हो सकती है।</li></ul></li><li><p><strong>एप्लिकेशन त्रुटियाँ</strong>:</p><ul><li><strong>त्रुटि प्रबंधन</strong>: सुनिश्चित करें कि फ़ाइल-संबंधी समस्याओं से निपटने के लिए आपके एप्लिकेशन में उचित त्रुटि प्रबंधन है।</li><li><strong>लॉग और डिबगिंग</strong>: अधिक विशिष्ट त्रुटि संदेशों के लिए एप्लिकेशन लॉग या डिबग आउटपुट की जाँच करें।</li></ul></li></ol>"


def get_excerpt(article, max_length=180):
    content = article.content.replace(
        "{{appname}}", app_context.config.get("site_name", "")
    ).replace("{{appmail}}", app_context.config.get("app_mail", ""))
    text = BeautifulSoup(content, "html.parser").get_text(" ", strip=True)

    if not text:
        return ""

    first, *rest = [p.strip() for p in text.split("।") if p.strip()]

    if len(first) < max_length and rest:
        return f"{first}। {rest[0]}।"

    return f"{first}।"



class ArticleService:

    @staticmethod
    async def serialize_article(article: _Article):
        await Article.add_prev_next_article(article)

        article.type = await TermsCache.get_by_id(article.type)
        article.parameter = await TermsCache.get_by_id(article.parameter)

        member_id = await app_context.setting.member("id")
        Likes.exists(article.id, member_id)

        article.feedback = (
            "article-like" if Likes.exists(article.id, member_id) else "feedback"
        )

        await get_artical_url(article)
        await enrich_article(article, excerpt=True, suggestion=True)

        # Replace placeholders in content
        article.content = article.content.replace(
            "{{appname}}", app_context.config.get("site_name", "")
        )
        article.content = article.content.replace(
            "{{appmail}}", app_context.config.get("app_mail", "")
        )

        dictionary = to_dict(article)
        dictionary.update(
            {
                "update_session_returns": {
                    "id": article.id,
                    "update_type": "article_metrics",
                    "update_option": ["rank", "views"],
                }
            }
        )

        dictionary.update(
            {
                "prev_article": await get_mini_article_json(
                    article.prev_article, excerpt=True
                ),
                "next_article": await get_mini_article_json(
                    article.next_article, excerpt=True
                ),
            }
        )

        return dictionary

    @staticmethod
    async def find_article(**more):
        article_query = app_context.db.query(Article)

        for key, value in more.items():
            if value is None:
                continue

            column = getattr(Article, key, None)
            if column is None:
                continue

            article_query = article_query.filter(column == value)

        article = article_query.filter(Article.status == "Publish").first()
        return (
            await ArticleService.serialize_article(
                await article.to_dataclass(category=True, like=True)
            )
            if article
            else None
        )

    @staticmethod
    async def get__articles(*, limit=10, conditions: list | None = None, **more):
        print("get__articles")
        # Fix Mutable list bug se bachne ke liye safe initialization
        local_conditions = list(conditions) if conditions else []

        # Dynamic conditions extract karna from **more
        remaining_kwargs = {}
        for key, value in more.items():
            if value is not None and hasattr(Article, key):
                local_conditions.append(getattr(Article, key) == value)
            else:
                remaining_kwargs[key] = value

        # Always ensure Published status filter
        local_conditions.append(Article.status == "Publish")

        # Fix Modern SQLAlchemy 2.0 select() Query Construction
        query = select(Article).where(*local_conditions).group_by(Article.id)

        # Secondary DB Instance resolve (if using active_secondary_db)
        db = await active_secondary_db()

        # Case Simple limit fetch without extra pagination/search query params
        if not remaining_kwargs:
            stmt = query.limit(limit)
            res = db.execute(stmt)
            if inspect.isawaitable(res):
                res = await res

            items = res.scalars().all()

            return [
                (
                    await get_mini_article_json(item, excerpt=True)
                    if inspect.iscoroutinefunction(get_mini_article_json)
                    else get_mini_article_json(item, excerpt=True)
                )
                for item in items
            ]

        # Case Full Paginated Execution with NewQueryPaginator
        data = await NewQueryPaginator.paginate(
            types="query",
            query=query,
            model=Article,
            limit=limit,
            db=db,
            transform=lambda item: get_mini_article_json(item, excerpt=True),
            **remaining_kwargs,
        )

        return data.records

    @classmethod
    async def get_filtered_articles(cls, *, limit=10, **more):

        data = await cls.get__articles(
            limit=limit,
            conditions=[Article.parameter != 0],
            **more,
        )

        return data

    @classmethod
    async def get_page_lists(cls, *, limit=10, **more):
        data = await cls.get__articles(
            limit=limit,
            conditions=[Article.parameter == 0],
            **more,
        )
        return data

    @staticmethod
    async def find_article_by_terms(*, terms_id, limit=10, desc=None, **more):

        if terms_id is None:
            return None

        # Extract terms_id if accidentally passed as Model/Object instance
        if hasattr(terms_id, "id"):
            terms_id = terms_id.id

        # Modern SQLAlchemy 2.0 select query
        query = (
            select(Article)
            .join(TermsRelationship, TermsRelationship.article_id == Article.id)
            .where(
                TermsRelationship.terms_id == terms_id,
                Article.status == "Publish",
            )
            .distinct()
        )

        db = await active_secondary_db()

        remaining_kwargs = {}
        for key, value in list(more.items()):
            if value is not None and (column := getattr(Article, key, None)):
                # FIX HERE: Agar value object hai to .id pass karein, otherwise plain value
                clean_value = (
                    getattr(value, "id", value) if hasattr(value, "id") else value
                )

                # Additional safety check: clean_value basic scalar (int/str/bool) hi hona chahiye
                if isinstance(clean_value, (int, str, float, bool)):
                    query = query.where(column == clean_value)
                else:
                    remaining_kwargs[key] = value
            else:
                remaining_kwargs[key] = value

        if desc is not None:
            remaining_kwargs["desc"] = desc

        # Paginated Execution
        data = await NewQueryPaginator.paginate(
            types="query",
            query=query,
            model=Article,
            limit=limit,
            db=db,
            transform=lambda item: get_mini_article_json(item, excerpt=True),
            **remaining_kwargs,
        )

        return data.records

    @staticmethod
    async def find_liked_article(member_id, **more):
        db = await active_secondary_db()
        query = (
            select(Article)
            .join(UserRelationships, UserRelationships.article_id == Article.id)
            .where(
                UserRelationships.users_id == member_id,
                Article.status == "Publish",
            )
        )

        data = await NewQueryPaginator.paginate(
            types="query",
            query=query,
            model=Article,
            transform=lambda item: get_mini_article_json(item, excerpt=True),
            **more,
        )
        return data.records
