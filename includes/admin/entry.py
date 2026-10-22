from includes.src.request import Request

from includes.core.globals.route_context import Route
from includes.database.connection import config_secondary_db
from includes.database.models.secondary import Beckup
from includes.database.models.utils import TimeStamp
from includes.schemas.cache.subject import SubjectCache
from includes.utils._sub import configure_page
from includes.admin.schemas.article import AdminArticleService
from includes.admin.schemas.books import ClassBooks
from includes.admin.schemas.courses import ClassCourses
from includes.admin.schemas.practice import AdminClassObjective
from includes.admin.schemas.member import IsMember
from includes.admin.schemas.syllabus import AClassSyllabus
from includes.admin.schemas.term import AdminClassTerms
from includes.core.globals.fun import random_string

from includes.database.dataclass.dataclass import serialize
from includes.core.globals.entry import app_context

from includes.core.globals.initialize import initialize_database
from includes.executers import enrich_request_response
from includes.schemas.cookie import Cookie
from includes.admin.schemas.media import ClassMedia
from includes.admin.function import Function
from includes.core.security import AUTH_TOKEN
from includes.utils.utils import get_post_value


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


cookies = "qh5DB6lIEAkPko48e7wK1nKwVE.0.CVgz2WSvry2Z8HlGza5LbsmzmObJMk"


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

    # async def roots(self, resource, subresource, detail, details):
    async def roots(self, request, roots: Route):

        if "dashboard" == roots.section:
            self.request.state.response["menu_position"] = 0
            self.request.state.response["container_title"] = "Dashboard"
            trending = await AdminArticleService.get_trending_articles(10)

            self.request.state.response["trending"] = trending
            configure_page(request.state.metadata, template="admin/dashboard")
            return

        if "analytics" == roots.section:
            self.request.state.response["menu_position"] = 1
            self.request.state.response["container_title"] = "Analytics"

            trending = await AdminArticleService.get_trending_articles(10)

            # total_views = sum(item['views'] for item in trending)
            # total_likes = sum(item['likes'] for item in trending)

            self.request.state.response["trending"] = trending
            self.request.state.metadata.template = "admin/analytics"
            return

        if "syllabus" == roots.section:
            self.request.state.response["menu_position"] = 2
            self.request.state.response["container_title"] = "Syllabus"
            self.request.state.metadata.template = await AClassSyllabus.index(roots)
            return

        if "courses" == roots.section:
            self.request.state.response["menu_position"] = 3
            self.request.state.response["container_title"] = "Syllabus"
            self.request.state.metadata.template = await ClassCourses.index(roots)
            return

        if "content" == roots.section:
            article_service = AdminArticleService(request)
            self.request.state.response["menu_position"] = 4
            self.request.state.response["container_title"] = "Content"
            self.request.state.metadata.template = await article_service.index(roots)
            return

        if "category" == roots.section:
            self.request.state.response["menu_position"] = 5
            self.request.state.response["container_title"] = "Categories"

            template = await AdminClassTerms(request).index(roots)
            self.request.state.metadata.template = template
            return

        if "books" == roots.section:
            self.request.state.response["menu_position"] = 6
            self.request.state.response["container_title"] = "Study Material"
            self.request.state.metadata.template = await ClassBooks.index(roots)
            return

        if "practice" == roots.section:
            admin_class_objective = AdminClassObjective(request)
            self.request.state.response["menu_position"] = 7
            self.request.state.response["container_title"] = "MCQ"
            self.request.state.metadata.template = await admin_class_objective.index(
                roots
            )
            return

        if "media" == roots.section:
            self.request.state.response["menu_position"] = 10
            self.request.state.response["container_title"] = "Media Files"
            self.request.state.metadata.template = await ClassMedia.index(roots)
            return

        if "backup" == roots.section:
            self.request.state.response["menu_position"] = 6
            self.request.state.response["container_title"] = "Data Beckup"
            db = await config_secondary_db()
            backup = db.query(Beckup).all()
            self.request.state.response["data_querys"] = [
                {
                    "id": item.id,
                    "title": item.title,
                    "types": item.types,
                    # "content" : item.content,
                    "date": TimeStamp.format_datetime(item.timestamp),
                }
                for item in backup
            ]

            self.request.state.metadata.template = "admin/backup"
            return

        if "member" == roots.section:
            self.request.state.response["menu_position"] = 11
            self.request.state.response["container_title"] = "Members"
            self.request.state.metadata.template = await IsMember.index(roots)
            return

        if "teacher-verify-indentity" == roots.section:

            self.request.state.response["menu_position"] = 12
            self.request.state.response["container_title"] = "Teacher Verify Indentity"
            await IsMember.teacher_indentity(request=request)

            self.request.state.metadata.template = "admin/teacher_verify_identity"
            return

        self.request.state.metadata.template = "redirect"
        self.request.state.metadata.redirect_url = "/admin/dashboard"
        return

    async def user_verifaction(self, state):

        coockesCode = "_cf_clearance"
        verifaction_ture = "TM5DB6lIEAkPko48e7wK1nKwVECVgz2WSvry2Z8HlGza5LbsmzmObJMk"
        verifaction_false = "FM5DB6lIEAkPko48eKwVECVgz2WSvry2Z87wK1nHlGza5LbsmzmObJMk"
        verifaction_code = self.request.state.cookie.get(coockesCode)

        if verifaction_code == verifaction_ture:
            return None

        if not verifaction_code:
            self.request.state.cookie.domain(coockesCode, verifaction_false, 1)

        if not state == "login":
            self.request.state.metadata.template = "redirect"
            self.request.state.metadata.redirect_url = "/admin/login"
            return True

        def otp_verifaction(otp):
            try:
                return int(otp) == 8257
            except:
                return None

        def password_verifaction(password):
            return password == "password"

        if self.request.is_post:
            otp = await get_post_value(self.request, "otp")
            password = await get_post_value(self.request, "password")

            otp__ver = otp_verifaction(otp)
            pass_ver = password_verifaction(password)

            self.request.state.response["error"] = (
                None if pass_ver else "You could not verify the password! 😌"
            )
            self.request.state.response["error"] = (
                None if otp__ver else "You can try once more time"
            )

            if otp__ver and pass_ver:
                self.request.state.cookie.domain(coockesCode, verifaction_ture, 1)
                return None

        self.request.state.metadata.template = "/admin/login"
        return True


# async def admin_init(resource, subresource, detail, details):
async def admin_init(request: Request = None, roots: Route = None):
    setting_data = _Andow(request=request).get()
    await initialize_database(request)

    admin = Admin(request)

    if await admin.user_verifaction(roots.section):
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

    await admin.roots(request, roots)
    return await enrich_request_response(request.state.response, request)
