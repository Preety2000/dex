from includes.core.globals.initialize import initialize_database
from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.schemas.search import Search

from includes.admin.entry import Admin
from includes.admin.api.actionForm import ActionForm
from includes.admin.api.schemas.category import AdminApiCategory
from includes.admin.api.schemas.insert import AdminInsurt
from includes.admin.api.schemas.subject import AdminApiSubject
from includes.utils.utils import get_post_value, json_null_response, json_response


class ADMIN_API:
    def __init__(self, request):
        self.request = request
        self.state = request.state
        self.security = _Security
        self.function = app_context.function
        self.admin = Admin()

    async def index(self):

        print(app_context.route)

        await initialize_database()

        if await Admin.user_verifaction(app_context.route.resource_type):
            return json_response("Session End! 😒")

        if "insert" == app_context.route.resource_type:
            return await AdminInsurt.exiute()

        if "category" == app_context.route.resource_type:
            if app_context.route.resource_slug:
                return await AdminApiCategory.execute(app_context.route.resource_slug)

            return []

        if "tags" == app_context.route.resource_type:
            if app_context.route.resource_slug:
                return await self.tags()

        if "subject" == app_context.route.resource_type:
            if app_context.route.resource_slug:
                return json_response(
                    await AdminApiSubject.execute(app_context.route.resource_slug)
                )

        if "content" == app_context.route.resource_type:
            if app_context.route.resource_slug:
                return await self.content()

        # Action Form Js Request
        if (
            app_context.route.resource_type == "auth"
            and app_context.route.resource_slug == "t"
        ):
            return await ActionForm.index(app_context.route.resource_type)

        return [
            app_context.route.resource_type,
            app_context.route.resource_slug,
            app_context.route.resource_type,
        ]

    async def content(self):
        tags = await get_post_value("tags")
        types = await get_post_value("type")
        slug = await get_post_value("slug")
        title = await get_post_value("title")
        content = await get_post_value("content")
        subject = await get_post_value("subject")
        excerpt = await get_post_value("excerpt")
        parameter = await get_post_value("parameter")
        category = await get_post_value("category[]")

        query = {
            "tags": tags,
            "slug": slug,
            "types": types,
            "title": title,
            "content": content,
            "subject": subject,
            "excerpt": excerpt,
            "parameter": parameter,
            "category": category,
        }

        return json_response([{"query": query, "fatching_key": "g.params.key"}, 200])

    async def tags(self):
        if "search" == app_context.route.resource_slug:
            search = Search(self.request)
            search_term = await get_post_value("q")
            suggestion_query = search.suggestion(search_term, 20)

            return json_response(
                [{"query": suggestion_query, "fatching_key": "g.params.key"}, 200]
            )

        return [app_context.route.resource_slug, str(self.admin.subject.get(True))]

    async def category(self):

        if "insert" == app_context.route.resource_slug:
            subject = await get_post_value("subject")
            if not subject:
                return json_null_response(
                    details="Subject is not selected please select subject.",
                    code="Xes00050",
                )

            subject = self.admin.subject.get(subject, True)

            if not subject:
                return json_null_response(
                    details="Subject is not reached please give db subject.",
                    code="Xes00051",
                )

            post_values = {
                "subject_id": subject.id,
                "name": await get_post_value("name"),
                "slug": await get_post_value("slug"),
                "topic": await get_post_value("topic"),
                "app_context.route.resource_type": await get_post_value(
                    "app_context.route.resource_type"
                ),
                "image_src": await get_post_value("image_src", "empty.png"),
                "description": await get_post_value("description", ""),
            }

            check = None
            for item in ["name", "slug"]:
                if not post_values.get(item):
                    check = item
                    break

            if check:
                return json_null_response(
                    details=f"{check} is not fill please fill the {check} box.",
                    code="Xes00050",
                )

            query = self.admin.terms.insert(post_values)
            if query.get("mcq_ex") == True:
                return json_null_response(
                    details=f"This category alerady exists with the id {query.get('id')}.",
                    code="Xes00052",
                )

            return json_response(
                [{"query": query, "fatching_key": "g.params.key"}, 200]
            )
