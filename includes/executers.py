import asyncio
import copy
import datetime as dt
from typing import Any
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from includes.core.deviceinfo import DeviceInfo
from includes.utils._sub import apply_session_updates, configure_page
from includes.db.dataclass import serialize, to_dict

from includes.core.cache import AppCache
from includes.core.config import app_context
from includes.core.security import _Security

from includes.core.metadata import MetaData, set_article_context
from includes.core.globals.initialize import initialize_database
from includes.dispatcher import STATIC_HANDLERS, RequestDispatcher

from includes.schemas.terms import ClassTerms
from includes.schemas.articles import ArticleService
from includes.schemas.objective import get_mcq_by_terms_id
from includes.schemas.cache.terms import TermsCache
from includes.services.member.member import ClassUser
from includes.route_handler import StaticRouteHandler
from includes.utils.utils import get_query_value


async def get_terms_by_resource_cached(resource_id):
    resources = AppCache.get("resource")
    if not resources:
        resources = {t.slug: t for t in await ClassTerms.get_all_record(resource=1)}
        AppCache.add("resource", resources)

    return resources.get(resource_id, None)


async def execute_home_page(roots: Any = None) -> dict[str, Any]:

    # Predicate lambda for filtering
    term_filter = lambda r: r.article_count > 0

    # Desktop Execution (Parallel DB Queries for Maximum Speed)
    configure_page(template="index", title="Welcome", suffix=True)

    terms_task = ClassTerms.get_all_record(limit=16, topic=1, bind=term_filter)
    articles_task = ArticleService.get_filtered_articles(limit=12, desc="id")

    # Both DB calls run concurrently
    all_term_list, articles = await asyncio.gather(terms_task, articles_task)

    return {
        "resource": "widget",
        "articles": articles,
        "category": to_dict(all_term_list),
    }


async def build_http_response(result, templates, request):
    try:
        # ---------------------------------------------------------
        # Track response timing safely
        # ---------------------------------------------------------
        end_time = dt.datetime.now()
        app_context.response["end_time"] = end_time

        start_time = app_context.response.get("start_time")
        if start_time:
            app_context.response["fetch_time"] = (end_time - start_time).total_seconds()

        # ---------------------------------------------------------
        # Direct responses
        # ---------------------------------------------------------
        if isinstance(result, str):
            return result

        if isinstance(result, (StreamingResponse, HTMLResponse)):
            return result

        # ---------------------------------------------------------
        # Non-dict response
        # ---------------------------------------------------------
        if not isinstance(result, dict):
            return result

        # ---------------------------------------------------------
        # Build template context
        # ---------------------------------------------------------
        template_context = dict(result)

        template_context.update(
            {
                "request": request,
                "security": _Security,
                "app_context": app_context,
                "response": app_context.response,
                "svg": getattr(app_context, "svg_lists", None),
                "config": getattr(app_context, "config", None),
                "function": getattr(app_context, "function", None),
            }
        )

        # ---------------------------------------------------------
        # Add metadata
        # ---------------------------------------------------------
        metadata = MetaData.to_dict()

        if isinstance(metadata, dict):
            template_context.update(metadata)

        # request must always remain the actual Request object
        template_context["request"] = request

        # ---------------------------------------------------------
        # Handle redirect
        # ---------------------------------------------------------
        redirect_url = MetaData.redirect_url

        if redirect_url:
            return templates.TemplateResponse(
                request=request,
                name="redirect.html",
                context={
                    "request": request,
                    "redirect": redirect_url,
                    "response": None,
                },
            )

        # ---------------------------------------------------------
        # Select template
        # ---------------------------------------------------------
        template_name = template_context.get("template")

        print("template_name", template_name)
        if not isinstance(template_name, str) or not template_name.strip():
            template_name = "error"

        template_name = template_name.strip()

        # ---------------------------------------------------------
        # HTTP status code
        # ---------------------------------------------------------
        status_code_map = {
            "query/working": 503,
            "error": 404,
        }

        status_code = status_code_map.get(template_name, 200)

        # ---------------------------------------------------------
        # Final safety check
        # ---------------------------------------------------------
        if not template_name:
            template_name = "mdftr"
            status_code = 404

        # request must be present in context
        template_context["request"] = request
        template_context["device_info"] = DeviceInfo.to_dict()

        print(f"Rendering template: {MetaData}")
        # ---------------------------------------------------------
        # Render template
        # ---------------------------------------------------------
        return templates.TemplateResponse(
            request=request,
            name=f"{template_name}.html",
            context=template_context,
            status_code=status_code,
        )

    except Exception as e:
        print(f"ERROR in build_http_response: " f"{type(e).__name__}: {e}")
        raise

    finally:
        # ---------------------------------------------------------
        # Clean session teardown
        # ---------------------------------------------------------
        if hasattr(app_context, "main_session"):
            try:
                app_context.main_session.close()
            except Exception as e:
                print(f"main_session close error: {e}")

        if hasattr(app_context, "secondary_session"):
            try:
                app_context.secondary_session.close()
            except Exception as e:
                print(f"secondary_session close error: {e}")


async def enrich_request_response(response):
    auth_session = await app_context.setting.member()
    response.update({"auth_session": auth_session})

    return response


async def handle_request_with_cache(*, allow_catch: bool = True, **binds):
    # Base initialization
    await initialize_database()

    route_type = app_context.route.scope_type
    app_context.response["resource"] = route_type
    MetaData.template = "error"

    # Pehle static routes check karein
    static_response = await StaticRouteHandler.handle_static_route(route_type)
    if static_response is not None:
        return static_response

    # Encrypted Cache Key generation
    request_url_str = str(app_context.request.url)
    encrypted_url = _Security.short_encode(request_url_str)

    # Cache Check & Fallback Handler Execution
    metadata, session = AppCache.get(encrypted_url, (None, None))

    if session and metadata:
        # Cache me se mile metadata se MetaData class ko update karein
        MetaData.update_from_dict(metadata)
    else:
        # Request execute karein aur updated MetaData.to_dict() ke saath cache karein
        handler = binds.get("callback", execute_request)
        session = await handler(app_context.route)
        if allow_catch is True:
            AppCache.add(encrypted_url, (MetaData.to_dict(), session))

    # Response Enrichment & Processing
    app_context.response = await enrich_request_response(app_context.response)

    # Deepcopy ki jagah shallow copy ya lightweight dictionary copy try karein agar session safe ho
    session_data = copy.deepcopy(session) if isinstance(session, dict) else session
    processed_response = await apply_session_updates(session_data)

    await set_article_context(processed_response)

    if isinstance(processed_response, dict):
        app_context.response.update(processed_response)

    return app_context.response


async def execute_request(roots=None):
    scope_type = app_context.route.scope_type

    # Edge Case: Custom route checking (like container/media)
    if scope_type == "container" and app_context.route.scope_slug == "media":
        return await RequestDispatcher.handle_container_media(app_context)

    # Check Static Handlers Registry (O(1) lookup)
    if scope_type in STATIC_HANDLERS:
        return await STATIC_HANDLERS[scope_type](app_context)

    # 3. Dynamic Query Execution (Resource Query Fallback)
    resource_query = await get_terms_by_resource_cached(scope_type)

    if resource_query:
        if not app_context.route.scope_slug:
            article = await ArticleService.get_filtered_articles(
                limit=12, desc="id", parameter=resource_query.id
            )
            configure_page(
                template="query/parameter", title=resource_query.name, suffix=True
            )
            return {"page_type": "page", "data_querys": article}

        if app_context.route.scope_slug == "tagged" and app_context.route.resource_type:
            resource = await TermsCache.get_by_slug(app_context.route.resource_type)

            if resource is None:
                return {}

            article = await ArticleService.find_article_by_terms(
                terms_id=resource.id,
                parameter=resource_query,
                desc="id",
                limit=12,
            )
            practice = await get_mcq_by_terms_id(
                terms_id=resource.id, limit=6, desc="id"
            )

            configure_page(
                template="query/tagged",
                title=f"Questions tagged [ {resource.name} ]",
            )

            return {
                "practice": practice,
                "page_type": "tagged",
                "data_querys": article,
                "terms_query": serialize(resource),
            }

        # Article Session
        response = await ArticleService.find_article(
            slug=app_context.route.scope_slug, parameter=resource_query.id
        )
        if response:
            types = response.get("type")
            response["reseant_parameter"] = await ArticleService.get_filtered_articles(
                parameter=resource_query.id, limit=10
            )
            if isinstance(types, dict) and types.get("Id"):
                response["reseant_type"] = await ArticleService.get_filtered_articles(
                    type=types["Id"], limit=10
                )
            configure_page(
                template="query/second_parameter", title=response["title"], suffix=True
            )
            return response

    # Fallback Article Lookup
    data = await ArticleService.find_article(slug=scope_type, parameter=0)
    if data:
        page_list = await ArticleService.get_page_lists(desc="id", limit=6)
        configure_page(template="query/page", title=data.get("title"))
        return {
            "page_type": "article",
            "data_querys": data,
            "page_list": page_list,
        }

    return {}


async def process_account(request=None):
    await initialize_database()

    MetaData.template = await ClassUser.get_template()
    app_context.response["resource"] = app_context.route.scope_type
    return await enrich_request_response(app_context.response)
