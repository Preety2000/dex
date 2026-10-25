from includes.utils._sub import configure_page
from includes.core.globals.route_context import Route
from includes.database.models.secondary import Beckup
from includes.database.connection import config_secondary_db
from includes.database.models.utils import TimeStamp
from includes.admin.schemas.article import AdminArticleService
from includes.admin.schemas.books import ClassBooks
from includes.admin.schemas.courses import ClassCourses
from includes.admin.schemas.practice import AdminClassObjective
from includes.admin.schemas.member import IsMember
from includes.admin.schemas.syllabus import AClassSyllabus
from includes.admin.schemas.term import AdminClassTerms
from includes.admin.schemas.media import ClassMedia


class Roots:
    def __init__(self, request):
        self.request = request
        self.response = request.state.response
        self.metadata = request.state.metadata

        # Section Configuration Mapping (Menu Position, Title, aur Handler Method)
        self.section_map = {
            "dashboard": (0, "Dashboard", self.handle_dashboard),
            "analytics": (1, "Analytics", self.handle_analytics),
            "syllabus": (2, "Syllabus", self.handle_syllabus),
            "courses": (3, "Courses", self.handle_courses),
            "content": (4, "Content", self.handle_content),
            "category": (5, "Categories", self.handle_category),
            "books": (6, "Study Material", self.handle_books),
            "practice": (7, "MCQ", self.handle_practice),
            "backup": (8, "Data Backup", self.handle_backup),
            "media": (10, "Media Files", self.handle_media),
            "member": (11, "Members", self.handle_member),
            "teacher-verify-indentity": (
                12,
                "Teacher Identity Verification",
                self.handle_teacher_verify,
            ),
        }

    async def process(self, route: Route):
        """Main entry point jo section ke mutabiq sahi handler run karega"""
        section = route.section
        config = self.section_map.get(section)

        if config:
            menu_position, container_title, handler = config
            self.response["menu_position"] = menu_position
            self.response["container_title"] = container_title
            await handler(route)
        else:
            self.metadata.template = "redirect"
            self.metadata.redirect_url = "/admin/dashboard"

    # =========================================================
    # HANDLER METHODS
    # =========================================================

    async def handle_dashboard(self, route):
        self.response["trending"] = await AdminArticleService.get_trending_articles(10)
        configure_page(self.metadata, template="admin/dashboard")

    async def handle_analytics(self, route):
        self.response["trending"] = await AdminArticleService.get_trending_articles(10)
        self.metadata.template = "admin/analytics"

    async def handle_syllabus(self, route):
        self.metadata.template = await AClassSyllabus(request=self.request).index(route)

    async def handle_courses(self, route):
        self.metadata.template = await ClassCourses(request=self.request).index()

    async def handle_content(self, route):
        self.metadata.template = await AdminArticleService(self.request).index(route)

    async def handle_category(self, route):
        self.metadata.template = await AdminClassTerms(self.request).index(route)

    async def handle_books(self, route):
        self.metadata.template = await ClassBooks(request=self.request).index(route)

    async def handle_practice(self, route):
        self.metadata.template = await AdminClassObjective(self.request).index(route)

    async def handle_media(self, route):
        self.metadata.template = await ClassMedia.index(route)

    async def handle_backup(self, route):
        db = await config_secondary_db()
        try:
            backup_items = db.query(Beckup).all()
            self.response["data_querys"] = [
                {
                    "id": item.id,
                    "title": item.title,
                    "types": item.types,
                    "date": TimeStamp.format_datetime(item.timestamp),
                }
                for item in backup_items
            ]
        finally:
            db.close()
        self.metadata.template = "admin/backup"

    async def handle_member(self, route):
        self.metadata.template = await IsMember(request=self.request).index(route)

    async def handle_teacher_verify(self, route):
        await IsMember(request=self.request).teacher_indentity()
        self.metadata.template = "admin/teacher_verify_identity"
