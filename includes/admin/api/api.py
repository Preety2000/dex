from includes.src.request import Request

from includes.core.globals.initialize import initialize_database
from includes.core.globals.entry import app_context
from includes.core.globals.route_context import Route
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
        self.security = _Security
        self.admin = Admin(request)

    async def index(self, request: Request = None, roots: Route = None):

        await initialize_database(request)

        if await Admin.user_verifaction(request.state.roote.entity):
            return json_response("Session End! 😒")

        if "insert" == request.state.roote.entity:
            return await AdminInsurt.exiute()

        if "category" == request.state.roote.entity:
            if request.state.roote.action:
                return await AdminApiCategory.execute(request.state.roote.action)

            return []

        if "tags" == request.state.roote.entity:
            if request.state.roote.action:
                return await self.tags()

        if "subject" == request.state.roote.entity:
            if request.state.roote.action:
                return json_response(
                    await AdminApiSubject.execute(request.state.roote.action)
                )

        if "content" == request.state.roote.entity:
            if request.state.roote.action:
                return await self.content()

        # Action Form Js Request
        if request.state.roote.entity == "auth" and request.state.roote.action == "t":
            return await ActionForm.index(request.state.roote.entity)

        return [
            request.state.roote.entity,
            request.state.roote.action,
            request.state.roote.entity,
        ]

    async def content(self):
        tags = await get_post_value(self.request, "tags")
        types = await get_post_value(self.request, "type")
        slug = await get_post_value(self.request, "slug")
        title = await get_post_value(self.request, "title")
        content = await get_post_value(self.request, "content")
        subject = await get_post_value(self.request, "subject")
        excerpt = await get_post_value(self.request, "excerpt")
        parameter = await get_post_value(self.request, "parameter")
        category = await get_post_value(self.request, "category[]")

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
        if "search" == self.request.state.roote.action:
            search = Search(self.request)
            search_term = await get_post_value(self.request, "q")
            suggestion_query = search.suggestion(search_term, 20)

            return json_response(
                [{"query": suggestion_query, "fatching_key": "g.params.key"}, 200]
            )

        return [self.request.state.roote.action, str(self.admin.subject.get(True))]

    async def category(self):

        if "insert" == self.request.state.roote.action:
            subject = await get_post_value(self.request, "subject")
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
                "name": await get_post_value(self.request, "name"),
                "slug": await get_post_value(self.request, "slug"),
                "topic": await get_post_value(self.request, "topic"),
                "request.state.roote.entity": await get_post_value(
                    self.request, "request.state.roote.entity"
                ),
                "image_src": await get_post_value(
                    self.request, "image_src", "empty.webp"
                ),
                "description": await get_post_value(self.request, "description", ""),
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
