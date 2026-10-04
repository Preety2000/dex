from includes.database.models.secondary import Beckup
from includes.database.models.utils import TimeStamp
from includes.schemas.cache.subject import SubjectCache
from includes.utils._sub import configure_page
from includes.admin.schemas.article import ArticleService
from includes.admin.schemas.books import ClassBooks
from includes.admin.schemas.courses import ClassCourses
from includes.admin.schemas.practice import ClassObjective
from includes.admin.schemas.member import IsMember
from includes.admin.schemas.syllabus import AClassSyllabus
from includes.admin.schemas.term import AsminClassTerms
from includes.core.globals.fun import random_string
from includes.core.metadata import MetaData
from includes.database.dataclass.dataclass import serialize
from includes.core.globals.entry import app_context
from includes.core.globals.initialize import initialize_database
from includes.executers import enrich_request_response
from includes.schemas.cookie import Cookie
from includes.schemas.router_schema import DynamicURLRoute
from includes.admin.schemas.media import ClassMedia
from includes.admin.function import Function
from includes.core.security import AUTH_TOKEN, _Security
from includes.utils.utils import get_post_value


class _Andow:
    KEY = "_ad_eSt"

    @classmethod
    def _read(cls):
        return AUTH_TOKEN.decode(app_context.cookie.get(cls.KEY)) or {}

    @classmethod
    def set(cls, key, value):
        data = cls._read()
        data[key] = value

        app_context.cookie.insert(cls.KEY, AUTH_TOKEN.encode(data))

        return data

    @classmethod
    def get(cls, key=None):
        data = cls._read()
        return data.get(key) if key else data

    @classmethod
    def res(cls, key=None):
        if key:
            data = cls._read()
            data.pop(key, None)

            app_context.cookie.insert(cls.KEY, AUTH_TOKEN.encode(data))
            return data

        app_context.cookie.delete(cls.KEY)
        return {}


cookies = "qh5DB6lIEAkPko48e7wK1nKwVE.0.CVgz2WSvry2Z8HlGza5LbsmzmObJMk"


class Admin:
    def __init__(self):
        # app_context.response   = app_context.response
        self.request = app_context.request
        self.function = app_context.function
        self.security = _Security

        app_context.response["error"] = None
        app_context.response["request"] = self.request

    async def setupRequestContextMiddleware(self, state):

        # Set up the necessary classes for later use
        self.cookie = Cookie(self.request)
        self.adminFunction = Function(state, self)
        self.key = random_string(20)
        return self

    # async def roots(self, resource, subresource, detail, details):
    async def roots(self, roots: DynamicURLRoute):

        # DynamicURLRoute(raw_path='evaluate', depth=1, scope_type='evaluate', scope_slug=None, resource_type=None, resource_slug=None, sub_action=None, child_entity=None, modifier=None, segments=['evaluate'])

        if "dashboard" == roots.scope_type:
            app_context.response["menu_position"] = 0
            app_context.response["container_title"] = "Dashboard"
            trending = await ArticleService.get_trending_articles(10)

            app_context.response["trending"] = trending
            configure_page(template="admin/dashboard")
            return

        if "analytics" == roots.scope_type:
            app_context.response["menu_position"] = 1
            app_context.response["container_title"] = "Analytics"

            trending = await ArticleService.get_trending_articles(10)

            # total_views = sum(item['views'] for item in trending)
            # total_likes = sum(item['likes'] for item in trending)

            app_context.response["trending"] = trending
            MetaData.template = "admin/analytics"
            return

        if "syllabus" == roots.scope_type:
            app_context.response["menu_position"] = 2
            app_context.response["container_title"] = "Syllabus"
            MetaData.template = await AClassSyllabus.index(roots)
            return

        if "courses" == roots.scope_type:
            app_context.response["menu_position"] = 3
            app_context.response["container_title"] = "Syllabus"
            MetaData.template = await ClassCourses.index(roots)
            return

        if "content" == roots.scope_type:
            app_context.response["menu_position"] = 4
            app_context.response["container_title"] = "Content"
            MetaData.template = await ArticleService.index(roots)
            return

        if "category" == roots.scope_type:
            app_context.response["menu_position"] = 5
            app_context.response["container_title"] = "Categories"

            template = await AsminClassTerms.index(roots)
            MetaData.template = template
            return

        if "books" == roots.scope_type:
            app_context.response["menu_position"] = 6
            app_context.response["container_title"] = "Study Material"
            MetaData.template = await ClassBooks.index(roots)
            return

        if "practice" == roots.scope_type:
            app_context.response["menu_position"] = 7
            app_context.response["container_title"] = "MCQ"
            MetaData.template = await ClassObjective.index(roots)
            return

        if "media" == roots.scope_type:
            app_context.response["menu_position"] = 10
            app_context.response["container_title"] = "Media Files"
            MetaData.template = await ClassMedia.index(roots)
            return

        if "backup" == roots.scope_type:
            app_context.response["menu_position"] = 6
            app_context.response["container_title"] = "Data Beckup"
            backup = app_context.db.query(Beckup).all()
            app_context.response["data_querys"] = [
                {
                    "id": item.id,
                    "title": item.title,
                    "types": item.types,
                    # "content" : item.content,
                    "date": TimeStamp.format_datetime(item.timestamp),
                }
                for item in backup
            ]

            MetaData.template = "admin/backup"
            return

        if "member" == roots.scope_type:
            app_context.response["menu_position"] = 11
            app_context.response["container_title"] = "Members"
            MetaData.template = await IsMember.index(roots)
            return

        if "teacher-verify-indentity" == roots.scope_type:

            app_context.response["menu_position"] = 12
            app_context.response["container_title"] = "Teacher Verify Indentity"
            await IsMember.teacher_indentity()

            MetaData.template = "admin/teacher_verify_identity"
            return

        MetaData.template = "redirect"
        MetaData.redirect_url = "/admin/dashboard"
        return

    @staticmethod
    async def user_verifaction(state):

        coockesCode = "_cf_clearance"
        verifaction_ture = "TM5DB6lIEAkPko48e7wK1nKwVECVgz2WSvry2Z8HlGza5LbsmzmObJMk"
        verifaction_false = "FM5DB6lIEAkPko48eKwVECVgz2WSvry2Z87wK1nHlGza5LbsmzmObJMk"
        verifaction_code = app_context.cookie.get(coockesCode)

        if verifaction_code == verifaction_ture:
            return None

        if not verifaction_code:
            app_context.cookie.domain(coockesCode, verifaction_false, 1)

        # MetaData.template = "admin/error"
        # return
        if not state == "login":
            MetaData.template = "redirect"
            MetaData.redirect_url = "/admin/login"
            return True

        def otp_verifaction(otp):
            try:
                return int(otp) == 8257
            except:
                return None

        def password_verifaction(password):
            return password == "password"

        if app_context.function.is_post():
            otp = await get_post_value("otp")
            password = await get_post_value("password")

            otp__ver = otp_verifaction(otp)
            pass_ver = password_verifaction(password)

            app_context.response["error"] = (
                None if pass_ver else "You could not verify the password! 😌"
            )
            app_context.response["error"] = (
                None if otp__ver else "You can try once more time"
            )

            if otp__ver and pass_ver:
                app_context.cookie.domain(coockesCode, verifaction_ture, 1)
                return None

        MetaData.template = "/admin/login"
        return True


# async def admin_init(resource, subresource, detail, details):
async def admin_init(roots: DynamicURLRoute):
    setting_data = _Andow.get()
    await initialize_database()

    if await Admin.user_verifaction(roots.scope_type):
        app_context.response["container_title"] = "Login"
        return await enrich_request_response(app_context.response)

    configure_page(template="admin/error")
    if int(setting_data.get("collapsed") or 0) == 1:
        app_context.response["collapsed_nav"] = "collapsed_nav"

    app_context.response["_andow"] = setting_data
    app_context.response["resource"] = roots.scope_type

    admin = Admin()
    app_context.response["subjects"] = serialize(await SubjectCache.get_all())
    app_context.response["Geolobal"] = serialize(
        await AsminClassTerms.get_all_terms_by_subject()
    )

    await admin.roots(roots)

    return await enrich_request_response(app_context.response)
