from includes.src.request import Request
from includes.schemas.cookie import Cookie
from includes.utils._sub import configure_page

from includes.core.security import AUTH_TOKEN
from includes.core.globals.route_context import Route
from includes.core.globals.fun import random_string
from includes.core.globals.initialize import initialize_database
from includes.schemas.cache.subject import SubjectCache

from includes.executers import enrich_request_response
from includes.database.dataclass.dataclass import serialize

from includes.admin.roots import Roots
from includes.admin.login import AdminLogin
from includes.admin.function import Function
from includes.admin.schemas.term import AdminClassTerms

cookies = "qh5DB6lIEAkPko48e7wK1nKwVE.0.CVgz2WSvry2Z8HlGza5LbsmzmObJMk"


class _Andow:
    KEY = "_ad_eSt"

    def __init__(self, request):
        self.request = request

    def _read(self):
        return AUTH_TOKEN.decode(self.request.state.cookie.get(self.KEY)) or {}

    def set(self, key, value):
        data = self._read()
        data[key] = value

        self.request.state.cookie.insert(self.KEY, AUTH_TOKEN.encode(data))
        return data

    def get(self, key=None):
        data = self._read()
        return data.get(key) if key else data

    def res(self, key=None):
        if key:
            data = self._read()
            data.pop(key, None)

            self.request.state.cookie.insert(self.KEY, AUTH_TOKEN.encode(data))
            return data

        self.request.state.cookie.delete(self.KEY)
        return {}


class Admin:
    def __init__(self, request):
        self.request = request
        request.state.response["error"] = None
        request.state.response["request"] = self.request

    async def setupRequestContextMiddleware(self, state):
        # Set up the necessary classes for later use
        self.cookie = Cookie(self.request)
        self.adminFunction = Function(state, self)
        self.key = random_string(20)
        return self

    async def roots_endpoint(self, request, route: Route):
        router = Roots(request)
        return await router.process(route)


async def admin_init(request: Request = None, roots: Route = None):
    setting_data = _Andow(request=request).get()
    login_sesion = AdminLogin(request=request)
    await initialize_database(request)

    admin = Admin(request)

    if "logout" == roots.section:
        await login_sesion.logout()
        request.state.metadata.template = "redirect"
        request.state.metadata.redirect_url = "/admin/login"
        return await enrich_request_response(request.state.response, request)

    if await login_sesion.user_verification(roots.section):
        request.state.response["container_title"] = "Login"
        return await enrich_request_response(request.state.response, request)

    configure_page(request.state.metadata, template="admin/error")
    if int(setting_data.get("collapsed") or 0) == 1:
        request.state.response["collapsed_nav"] = "collapsed_nav"

    request.state.response["_andow"] = setting_data
    request.state.response["resource"] = roots.section
    request.state.response["subjects"] = serialize(await SubjectCache.get_all())
    request.state.response["Geolobal"] = serialize(
        await AdminClassTerms.get_all_terms_by_subject()
    )

    await admin.roots_endpoint(request, roots)
    return await enrich_request_response(request.state.response, request)
