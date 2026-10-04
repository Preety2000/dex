from includes.admin.modals import checked, emptyMessage
from includes.core.globals.coreutils import is_empty, slugify
from includes.core.globals.entry import app_context
from includes.core.metadata import MetaData
from includes.database.models.owner import Subject
from includes.database.models.secondary import Syllabus, University
from includes.schemas.router_schema import DynamicURLRoute
from includes.utils.utils import get_post_value


class AClassSyllabus:

    # JSON

    @staticmethod
    def json(query):
        if query is None:
            return None

        return {
            "id": query.id,
            "slug": query.slug,
            "title": query.title,
            "content": query.content,
            "subject": query.subject,
            "university": query.university,
            "timestamp": query.timestamp,
        }

    # GET

    @classmethod
    def get(cls, query=None, raw=False):
        db_query = app_context.db.query(Syllabus)

        # Return all
        if query is True:
            return [cls.json(item) for item in db_query.all()]

        if query is None:
            return None

        # Find by id / slug
        syllabus = db_query.filter(
            (Syllabus.id == query) | (Syllabus.slug == query)
        ).first()

        if raw:
            return syllabus

        return cls.json(syllabus)

    # INSERT

    @classmethod
    def insert(cls, data):
        if app_context.response["error"]:
            return data

        slug = data.get("slug") or data.get("title")

        if not slug:
            return data

        slug = slugify(slug)

        # Duplicate slug
        if cls.get(slug, raw=True):
            app_context.response["pop_message"] = "This syllabus already exists."
            return data

        subject = data.get("subject")
        university = data.get("university")

        syllabus = Syllabus(
            slug=slug,
            title=data.get("title"),
            subject=int(subject) if subject else 0,
            university=int(university) if university else 0,
            content=data.get("content"),
        )

        app_context.db.add(syllabus)
        app_context.db.commit()

        data["slug"] = slug
        data["redirect"] = True

        return data

    # UPDATE

    @classmethod
    def update(cls, data):
        if app_context.response["error"]:
            return data

        item_id = app_context.function.getRequestInt("item")

        syllabus = cls.get(item_id, raw=True)

        if syllabus is None:
            app_context.response["pop_message"] = "Syllabus not found."
            return data

        slug = data.get("slug") or syllabus.slug

        syllabus.slug = slugify(slug)

        if data.get("title") is not None:
            syllabus.title = data["title"]

        if data.get("subject"):
            syllabus.subject = int(data["subject"])

        if data.get("university"):
            syllabus.university = int(data["university"])

        if data.get("content") is not None:
            syllabus.content = data["content"]

        app_context.db.commit()

        app_context.response["message"] = "Updated <a href='/admin/syllabus'>Back</a>"

        data["redirect"] = True

        return data

    # DELETE

    @classmethod
    def delete(cls, data):
        item_id = data.get("id")

        if not item_id:
            item_id = app_context.function.getRequestInt("item")

        syllabus = cls.get(item_id, raw=True)

        if syllabus is None:
            app_context.response["pop_message"] = "Syllabus not found."
            return data

        try:
            app_context.db.delete(syllabus)
            app_context.db.commit()

        except Exception:
            app_context.db.rollback()

            app_context.response["pop_message"] = (
                "Syllabus could not be deleted. " "Error code Xe742524"
            )

            return data

        data["redirect"] = True

        return data

    # COLLECTION DATA

    @classmethod
    def addCollection(cls, data):
        subject_id = data.get("subject") or 0
        university_id = data.get("university") or 0

        try:
            subject_id = int(subject_id)
        except (TypeError, ValueError):
            subject_id = 0

        try:
            university_id = int(university_id)
        except (TypeError, ValueError):
            university_id = 0

        # Subjects
        subjects = []

        for subject in app_context.db.query(Subject).all():
            item = {
                "id": subject.id,
                "name": subject.name,
                "slug": subject.slug,
            }

            if subject.id == subject_id:
                data["subject_name"] = subject.name

            subjects.append(item)

        app_context.response["subjects"] = subjects

        # Universities
        universities = []

        for university in app_context.db.query(University).all():
            item = {
                "id": university.id,
                "name": university.name,
                "slug": university.slug,
            }

            if university.id == university_id:
                data["university_name"] = university.name

            universities.append(item)

        app_context.response["universitys"] = universities

        return data

    # VALIDATION

    @classmethod
    async def _get_form_data(cls):
        fields = [
            "title",
            "slug",
            "subject",
            "university",
            "content",
        ]

        data = await get_post_value(
            fields,
            "",
        )

        # Generate slug from title if slug is empty
        slug = data.get("slug")

        if is_empty(slug):
            slug = data.get("title")

        if slug:
            data["slug"] = slugify(slug)

        # Required fields
        for field, value in data.items():
            if is_empty(value) and field != "content":
                app_context.response["error"] = app_context.response[
                    "error"
                ] or emptyMessage(field, "")

        return data

    # INDEX

    @classmethod
    async def index(cls, roots: DynamicURLRoute):
        item_id = app_context.function.getRequestInt("item")
        is_post = app_context.function.is_post()

        actions = {
            "insert": cls.insert,
            "update": cls.update,
            "delete": cls.delete,
        }

        # -----------------------------------------------------
        # INSERT / UPDATE / DELETE
        # -----------------------------------------------------

        if roots.scope_slug in actions:
            action = actions[roots.scope_slug]

            # Existing data for update/delete
            data = {}

            if roots.scope_slug in ("update", "delete"):
                data = (
                    cls.get(
                        item_id,
                        raw=False,
                    )
                    or {}
                )

            # POST data
            if is_post:
                data = await cls._get_form_data()

            # Empty form for GET
            elif not data:
                data = {
                    "title": "",
                    "slug": "",
                    "subject": "",
                    "university": "",
                    "content": "",
                }

            # Execute action
            if is_post:
                result = action(data)

                if result is None:
                    result = data

                if result.get("redirect"):
                    MetaData.redirect_url = "/admin/syllabus"
                    return "redirect"

                data = result

            app_context.response["data_querys"] = cls.addCollection(data)

            return "admin/add_syllabus"

        # -----------------------------------------------------
        # LIST
        # -----------------------------------------------------

        app_context.response["data_querys"] = cls.get(True)

        return "admin/syllabus"
