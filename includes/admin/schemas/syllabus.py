from includes.admin.modals import checked, emptyMessage
from includes.core.globals.coreutils import is_empty, slugify
from includes.core.globals.route_context import Route
from includes.database.connection import db
from includes.database.models.primary import Subject
from includes.database.models.secondary import Syllabus, University
from includes.utils.utils import get_post_value


class AClassSyllabus:
    def __init__(self, request):
        self.request = request

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

    def get(self, query=None, raw=False):
        db_query = db.query(Syllabus)

        # Return all
        if query is True:
            return [self.json(item) for item in db_query.all()]

        if query is None:
            return None

        # Find by id / slug
        syllabus = db_query.filter(
            (Syllabus.id == query) | (Syllabus.slug == query)
        ).first()

        if raw:
            return syllabus

        return self.json(syllabus)

    # INSERT

    def insert(self, data):
        if self.request.state.response["error"]:
            return data

        slug = data.get("slug") or data.get("title")

        if not slug:
            return data

        slug = slugify(slug)

        # Duplicate slug
        if self.get(slug, raw=True):
            self.request.state.response["pop_message"] = "This syllabus already exists."
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

        db.add(syllabus)
        db.commit()

        data["slug"] = slug
        data["redirect"] = True

        return data

    # UPDATE

    def update(self, data):
        if self.request.state.response["error"]:
            return data

        item_id = get_post_value(self.request, "item")

        syllabus = self.get(item_id, raw=True)

        if syllabus is None:
            self.request.state.response["pop_message"] = "Syllabus not found."
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

        db.commit()

        self.request.state.response["message"] = (
            "Updated <a href='/admin/syllabus'>Back</a>"
        )

        data["redirect"] = True

        return data

    # DELETE

    def delete(self, data):
        item_id = data.get("id")

        if not item_id:
            item_id = get_post_value(self.request, "item")

        syllabus = self.get(item_id, raw=True)

        if syllabus is None:
            self.request.state.response["pop_message"] = "Syllabus not found."
            return data

        try:
            db.delete(syllabus)
            db.commit()

        except Exception:
            db.rollback()

            self.request.state.response["pop_message"] = (
                "Syllabus could not be deleted. " "Error code Xe742524"
            )

            return data

        data["redirect"] = True

        return data

    # COLLECTION DATA

    def addCollection(self, data):
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

        for subject in db.query(Subject).all():
            item = {
                "id": subject.id,
                "name": subject.name,
                "slug": subject.slug,
            }

            if subject.id == subject_id:
                data["subject_name"] = subject.name

            subjects.append(item)

        self.request.state.response["subjects"] = subjects

        # Universities
        universities = []

        for university in db.query(University).all():
            item = {
                "id": university.id,
                "name": university.name,
                "slug": university.slug,
            }

            if university.id == university_id:
                data["university_name"] = university.name

            universities.append(item)

        self.request.state.response["universitys"] = universities

        return data

    # VALIDATION

    async def _get_form_data(self):
        fields = [
            "title",
            "slug",
            "subject",
            "university",
            "content",
        ]

        data = await get_post_value(
            self.request,
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
                self.request.state.response["error"] = self.request.state.response[
                    "error"
                ] or emptyMessage(field, "")

        return data

    # INDEX

    async def index(self, roots: Route):
        item_id = get_post_value(self.request, "item")
        is_post = self.request.is_post

        actions = {
            "insert": self.insert,
            "update": self.update,
            "delete": self.delete,
        }

        # -----------------------------------------------------
        # INSERT / UPDATE / DELETE
        # -----------------------------------------------------

        if roots.scope in actions:
            action = actions[roots.scope]

            # Existing data for update/delete
            data = {}

            if roots.scope in ("update", "delete"):
                data = (
                    self.get(
                        item_id,
                        raw=False,
                    )
                    or {}
                )

            # POST data
            if is_post:
                data = await self._get_form_data()

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
                    self.request.state.metadata.redirect_url = "/admin/syllabus"
                    return "redirect"

                data = result

            self.request.state.response["data_querys"] = self.addCollection(data)

            return "admin/add_syllabus"

        # -----------------------------------------------------
        # LIST
        # -----------------------------------------------------

        self.request.state.response["data_querys"] = self.get(True)

        return "admin/syllabus"
