from sqlalchemy import asc

from includes.database.connection import db
from includes.core.globals.coreutils import slugify
from includes.core.globals.entry import app_context
from includes.core.globals.route_context import Route
from includes.database.models.secondary import Courses
from includes.utils.utils import get_post_value


class ClassCourses:

    def __init__(self, request):
        self.request = request

    # JSON

    @staticmethod
    def json(query):
        if query is None:
            return None

        return {
            "id": query.id,
            "title": query.title,
            "slug": query.slug,
            "content": query.content,
            "university": query.university,
        }

    def get(self, query=None, raw=False):
        courses = db.query(Courses)

        # Get all courses
        if query is True:
            items = courses.order_by(asc(Courses.title)).all()

            return [self.json(item) for item in items]

        if query is None:
            return None

        # Find by id / slug / title
        course = courses.filter(
            (Courses.id == query) | (Courses.slug == query) | (Courses.title == query)
        ).first()

        if raw:
            return course

        return self.json(course)

    # INSERT

    def insert(self, data):
        if self.request.state.response["error"]:
            return data

        title = data.get("title")
        slug = data.get("slug") or title
        content = data.get("content")
        university = data.get("university")

        if not title or not slug:
            return data

        slug = slugify(slug)

        # Check duplicate slug
        if self.get(slug, raw=True):
            result = self.get(slug)

            if result:
                result["mcq_ex"] = True

            return result

        # Check duplicate title
        if self.get(title, raw=True):
            result = self.get(title)

            if result:
                result["mcq_ex"] = True

            return result

        try:
            course = Courses(
                title=title,
                slug=slug,
                content=content,
                university=(int(university) if university else 0),
            )

            db.add(course)
            db.commit()

        except Exception:
            db.rollback()

            self.request.state.response["pop_message"] = "Course could not be created."

            return data

        result = self.json(course)

        if result:
            result["mcq_ex"] = True

        return result

    # UPDATE

    def update(self, data):
        if self.request.state.response["error"]:
            return data

        item_id = data.get("id")

        if not item_id:
            item_id = get_post_value(self.request, "item")

        course = self.get(item_id, raw=True)

        if course is None:
            return "Not any query found."

        title = data.get("title")
        slug = data.get("slug")
        content = data.get("content")
        university = data.get("university")

        if title is not None:
            course.title = title

        if slug:
            course.slug = slugify(slug)

        if content is not None:
            course.content = content

        if university:
            course.university = int(university)

        try:
            db.commit()

        except Exception:
            db.rollback()

            self.request.state.response["pop_message"] = "Course could not be updated."

            return data

        return "Update Successfully"

    # DELETE

    def delete(self, data):
        item_id = data.get("id")

        if not item_id:
            item_id = get_post_value(self.request, "item")

        course = self.get(item_id, raw=True)

        if course is None:
            return "Not any query found."

        try:
            db.delete(course)
            db.commit()

        except Exception:
            db.rollback()

            self.request.state.response["pop_message"] = "Course could not be deleted."

            return data

        return {
            "redirect": True,
        }

    # INDEX

    async def index(self):

        # -----------------------------------------------------
        # API POST
        # -----------------------------------------------------

        if self.request.method == "POST" and self.request.query_params("key"):
            parameter = getattr(
                app_context.admin,
                "parameter",
                None,
            )

            if not parameter:
                return [{"error": "Invalid API parameter."}]

            bind_function = getattr(
                self,
                parameter,
                None,
            )

            if self.request.state.response["error"]:
                return [{"error": self.request.state.response["error"]}]

            if callable(bind_function):
                result = bind_function(app_context.data_querys)

                return [{"bind": result}]

            return [{"error": "Session error, time out."}]

        # -----------------------------------------------------
        # ADMIN
        # -----------------------------------------------------

        self.request.state.response["data_querys"] = self.get(True)

        return "admin/courses"
