from sqlalchemy import asc

from includes.core.globals.entry import app_context

from includes.core.globals.coreutils import slugify
from includes.core.globals.route_context import Route
from includes.database.connection import db
from includes.database.models.secondary import Courses


class ClassCourses:

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

    # GET

    @classmethod
    def get(cls, query=None, raw=False):
        courses = db.query(Courses)

        # Get all courses
        if query is True:
            items = courses.order_by(asc(Courses.title)).all()

            return [cls.json(item) for item in items]

        if query is None:
            return None

        # Find by id / slug / title
        course = courses.filter(
            (Courses.id == query) | (Courses.slug == query) | (Courses.title == query)
        ).first()

        if raw:
            return course

        return cls.json(course)

    # INSERT

    @classmethod
    def insert(cls, data):
        if request.state.response["error"]:
            return data

        title = data.get("title")
        slug = data.get("slug") or title
        content = data.get("content")
        university = data.get("university")

        if not title or not slug:
            return data

        slug = slugify(slug)

        # Check duplicate slug
        if cls.get(slug, raw=True):
            result = cls.get(slug)

            if result:
                result["mcq_ex"] = True

            return result

        # Check duplicate title
        if cls.get(title, raw=True):
            result = cls.get(title)

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

            request.state.response["pop_message"] = "Course could not be created."

            return data

        result = cls.json(course)

        if result:
            result["mcq_ex"] = True

        return result

    # UPDATE

    @classmethod
    def update(cls, data):
        if request.state.response["error"]:
            return data

        item_id = data.get("id")

        if not item_id:
            item_id = get_post_value(request, "item")

        course = cls.get(item_id, raw=True)

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

            request.state.response["pop_message"] = "Course could not be updated."

            return data

        return "Update Successfully"

    # DELETE

    @classmethod
    def delete(cls, data):
        item_id = data.get("id")

        if not item_id:
            item_id = get_post_value(request, "item")

        course = cls.get(item_id, raw=True)

        if course is None:
            return "Not any query found."

        try:
            db.delete(course)
            db.commit()

        except Exception:
            db.rollback()

            request.state.response["pop_message"] = "Course could not be deleted."

            return data

        return {
            "redirect": True,
        }

    # INDEX

    @classmethod
    async def index(cls, roots: Route):

        # -----------------------------------------------------
        # API POST
        # -----------------------------------------------------

        if request.method == "POST" and request.query_params("key"):
            parameter = getattr(
                app_context.admin,
                "parameter",
                None,
            )

            if not parameter:
                return [{"error": "Invalid API parameter."}]

            bind_function = getattr(
                cls,
                parameter,
                None,
            )

            if request.state.response["error"]:
                return [{"error": request.state.response["error"]}]

            if callable(bind_function):
                result = bind_function(app_context.data_querys)

                return [{"bind": result}]

            return [{"error": "Session error, time out."}]

        # -----------------------------------------------------
        # ADMIN
        # -----------------------------------------------------

        request.state.response["data_querys"] = cls.get(True)

        return "admin/courses"
