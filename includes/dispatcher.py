import os
import json


from includes.schemas.trending import ArticleTrendingService
from includes.utils._sub import configure_page
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
from includes.core.repo.dir_manager import folder
from includes.core.globals.entry import app_context


class RequestDispatcher:
    """
    Handles request routing based on app_context scope_type.
    Replaces long if-elif chains with clean strategy pattern/dispatcher.
    """

    @staticmethod
    async def handle_success(request):
        request.state.metadata.template = "widget/welcome"
        return {"page_type": "page"}

    @staticmethod
    async def handle_exam(request):
        return await process_exam(request)

    @staticmethod
    async def handle_allsvg(request):
        request.state.svg_lists = await load_svg_files()
        request.state.metadata.title = "All Svg"
        request.state.metadata.template = "allsvg"
        return {"page_type": "page"}

    @staticmethod
    async def handle_liked_questions(request):
        return await ClassUser(request).liked_questions()

    @staticmethod
    async def handle_working_query(request):
        configure_page(
            request.state.metadata,
            template="query/working",
            title="Internal Server Error",
        )
        return {"page_type": "page"}

    @staticmethod
    async def handle_inbox(request):
        configure_page(request.state.metadata, title="Inbox", template="query/inbox")
        return {"page_type": "page"}

    @staticmethod
    async def handle_sitemap_update(request):
        sitemap_url = await Sitemap.index()
        file_path = os.path.join(folder.static_json, "sitemap.json")

        with open(file_path, "w") as file:
            json.dump(sitemap_url, file, indent=4)

        configure_page(request.state.metadata, title="Sitemap Update", suffix=True)
        return {"message": "Sitemap Update Successfully"}

    @staticmethod
    async def handle_trending(request):
        configure_page(
            request.state.metadata,
            template="query/trending",
            title="Trending",
            suffix=True,
        )
        return {
            "page_type": "trending_page",
            "data_querys": await ArticleTrendingService.get_articles(
                limit=12, request=request
            ),
        }

    @staticmethod
    async def handle_topic(request):
        configure_page(
            request.state.metadata, template="query/topic", title="Topic", suffix=True
        )
        return {
            "page_type": "category_page",
            "category": await ClassSubject.get_with_terms(),
        }

    @staticmethod
    async def handle_ls(request):
        datatype = "cot"
        sub = None
        request.state.metadata.template = "list_category"
        if request.state.roote.scope:
            sub = await SubjectCache.get_by_id(int(request.state.roote.scope))
            subject_list = await TermsCache.get_by_subject(
                int(request.state.roote.scope)
            )
        else:
            datatype = "subject"
            subject_list = await SubjectCache.get_all()

        return {
            "datatype": datatype,
            "data": subject_list,
            "sub": sub,
        }

    @staticmethod
    async def handle_practice(request):
        mcq_categorys = await ClassSubject.get_with_terms()
        configure_page(
            request.state.metadata, title=f"{app_context.function.utc('MCQ Question')}"
        )

        if request.state.roote.scope and request.state.roote.scope != "tagged":
            if request.state.roote.entity:
                category = ClassTerms.get(topic=1, slug=request.state.roote.scope)
                data_querys = await ClassObjective.get(
                    request=request,
                    id=int(request.state.roote.entity),
                    terms_id=category.get("id"),
                )
            else:
                data_querys = await ClassObjective.get(
                    request=request, id=int(request.state.roote.scope)
                )

            if data_querys:
                request.state.metadata.template = "query/mcq_view"
                configure_page(
                    request.state.metadata,
                    title=f"{data_querys.get('question')} • {app_context.function.utc('MCQ Question')}",
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
            request.state.roote.entity,
            request=request,
            limit=10,
            asc="question",
        )
        if quiz_query:
            request.state.metadata.template = "query/practice"
            return {
                "page_type": "category_page",
                "quiz_query": quiz_query,
                "result_type": result_type["name"],
                "mcq_categorys": mcq_categorys,
            }
        return {}

    @staticmethod
    async def handle_recent(request):
        if request.state.divice_info.is_mobile is False:
            configure_page(
                request.state.metadata,
                template="query/parameter",
                title="Latest Additions",
                suffix=True,
            )
            article = await ArticleService.get_filtered_articles(
                limit=12, desc="id", request=request
            )
            return {"page_type": "page", "data_querys": article}

        configure_page(
            request.state.metadata,
            template="index.mobile",
            title="Latest Additions",
            suffix=True,
        )
        return {"page_type": "page"}

    @staticmethod
    async def handle_syllabus(request):
        syllabus = await ClassSyllabus.index(
            request.state.roote.scope, request.state.roote.entity
        )
        request.state.metadata.template = syllabus
        return {}

    @staticmethod
    async def handle_settings(request):
        q = request.state.setting.handle_request(request.state.roote.scope)
        configure_page(
            request.state.metadata,
            template="query/setting",
            title="Setting",
            suffix=True,
        )

        return q

    @staticmethod
    async def handle_download(request):
        configure_page(
            request.state.metadata,
            template=ClassDownload.index(),
            title="Download App",
            suffix=True,
        )
        return {}

    @staticmethod
    async def handle_container_media(request):
        request.state.metadata.template = "admin/media_container"
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
