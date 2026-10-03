import os
import json

from includes.schemas.trending import ArticleTrendingService
from includes.utils._sub import configure_page
from includes.core.metadata import MetaData
from includes.function import load_svg_files
from includes.schemas.articles import ArticleService
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.cache.terms import TermsCache
from includes.schemas.download import ClassDownload
from includes.schemas.objective import ClassObjective
from includes.schemas.sitemap import Sitemap
from includes.schemas.subject import ClassSubject
from includes.schemas.syllabus import ClassSyllabus
from includes.schemas.terms import ClassTerms
from includes.services.exam.exam import process_exam
from includes.services.member.member import ClassUser


class RequestDispatcher:
    """
    Handles request routing based on app_context scope_type.
    Replaces long if-elif chains with clean strategy pattern/dispatcher.
    """

    @staticmethod
    async def handle_success(ctx):
        MetaData.template = "widget/welcome"
        return {"page_type": "page"}

    @staticmethod
    async def handle_exam(ctx):
        return await process_exam(ctx.route)

    @staticmethod
    async def handle_allsvg(ctx):
        ctx.svg_lists = await load_svg_files(ctx)
        MetaData.title = "All Svg"
        MetaData.template = "allsvg"
        return {"page_type": "page"}

    @staticmethod
    async def handle_liked_questions(ctx):
        return await ClassUser.liked_questions()

    @staticmethod
    async def handle_working_query(ctx):
        configure_page(template="query/working", title="Internal Server Error")
        return {"page_type": "page"}

    @staticmethod
    async def handle_inbox(ctx):
        configure_page(title="Inbox", template="query/inbox")
        return {"page_type": "page"}

    @staticmethod
    async def handle_sitemap_update(ctx):
        sitemap_url = await Sitemap.index()
        file_path = os.path.join(ctx.folder.static_json, "sitemap.json")

        with open(file_path, "w") as file:
            json.dump(sitemap_url, file, indent=4)

        configure_page(title="Sitemap Update", suffix=True)
        return {"message": "Sitemap Update Successfully"}

    @staticmethod
    async def handle_trending(ctx):
        configure_page(template="query/trending", title="Trending", suffix=True)
        return {
            "page_type": "trending_page",
            "data_querys": await ArticleTrendingService.get_articles(limit=12),
        }

    @staticmethod
    async def handle_topic(ctx):
        configure_page(template="query/topic", title="Topic", suffix=True)
        return {
            "page_type": "category_page",
            "category": await ClassSubject.get_with_terms(),
        }

    @staticmethod
    async def handle_ls(ctx):
        datatype = "cot"
        sub = None
        MetaData.template = "list_category"
        if ctx.route.scope_slug:
            sub = await SubjectCache.get_by_id(int(ctx.route.scope_slug))
            subject_list = await TermsCache.get_by_subject(int(ctx.route.scope_slug))
        else:
            datatype = "subject"
            subject_list = await SubjectCache.get_all()

        return {
            "datatype": datatype,
            "data": subject_list,
            "sub": sub,
        }

    @staticmethod
    async def handle_practice(ctx):
        mcq_categorys = await ClassSubject.get_with_terms()
        configure_page(title=f"{ctx.function.utc('MCQ Question')}")

        if ctx.route.scope_slug and ctx.route.scope_slug != "tagged":
            if ctx.route.resource_type:
                category = ClassTerms.get(topic=1, slug=ctx.route.scope_slug)
                data_querys = await ClassObjective.get(
                    id=int(ctx.route.resource_type), terms_id=category.get("id")
                )
            else:
                data_querys = await ClassObjective.get(id=int(ctx.route.scope_slug))

            if data_querys:
                MetaData.template = "query/mcq_view"
                configure_page(
                    title=f"{data_querys.get('question')} • {ctx.function.utc('MCQ Question')}"
                )
                return {
                    "page_type": "category_page",
                    "data_querys": data_querys,
                    "mcq_categorys": mcq_categorys,
                    "update_session_returns": {
                        "id": data_querys.get("id"),
                        "update_type": "practice_metrics",
                        "update_option": ["views"],
                    },
                }
            return {}

        quiz_query, result_type = await ClassObjective.getmcq_list(
            ctx.route.resource_type, limit=10, asc="question"
        )
        if quiz_query:
            MetaData.template = "query/practice"
            return {
                "page_type": "category_page",
                "quiz_query": quiz_query,
                "result_type": result_type["name"],
                "mcq_categorys": mcq_categorys,
            }
        return {}

    @staticmethod
    async def handle_recent(ctx):
        device = MetaData.device_info
        if device.get("is_mobile") is False:
            configure_page(
                template="query/parameter", title="Latest Additions", suffix=True
            )
            article = await ArticleService.get_filtered_articles(limit=12, desc="id")
            return {"page_type": "page", "data_querys": article}

        configure_page(template="index.mobile", title="Latest Additions", suffix=True)
        return {"page_type": "page"}

    @staticmethod
    async def handle_syllabus(ctx):
        syllabus = await ClassSyllabus.index(
            ctx.route.scope_slug, ctx.route.resource_type
        )
        MetaData.template = syllabus
        return {}

    @staticmethod
    async def handle_settings(ctx):
        q = ctx.setting.handle_request(ctx.route.scope_slug)
        configure_page(template="query/setting", title="Setting", suffix=True)

        return q

    @staticmethod
    async def handle_download(ctx):
        configure_page(
            template=ClassDownload.index(), title="Download App", suffix=True
        )
        return {}

    @staticmethod
    async def handle_container_media(ctx):
        MetaData.template = "admin/media_container"
        return {}


# Handlers Registry Mapping
STATIC_HANDLERS = {
    "success": RequestDispatcher.handle_success,
    "exam": RequestDispatcher.handle_exam,
    "allsvg": RequestDispatcher.handle_allsvg,
    "liked-questions": RequestDispatcher.handle_liked_questions,
    "courses": RequestDispatcher.handle_working_query,
    "shopping": RequestDispatcher.handle_working_query,
    "inbox": RequestDispatcher.handle_inbox,
    "sitemap_update": RequestDispatcher.handle_sitemap_update,
    "trending": RequestDispatcher.handle_trending,
    "ls": RequestDispatcher.handle_ls,
    "topic": RequestDispatcher.handle_topic,
    "practice": RequestDispatcher.handle_practice,
    "resent": RequestDispatcher.handle_recent,
    "syllabus": RequestDispatcher.handle_syllabus,
    "settings": RequestDispatcher.handle_settings,
    "download": RequestDispatcher.handle_download,
}
