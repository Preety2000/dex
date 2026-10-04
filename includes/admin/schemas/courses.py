from sqlalchemy import asc

from includes.core.globals.entry import app_context
from includes.core.globals.coreutils import slugify
from includes.database.models.secondary import Courses
from includes.schemas.router_schema import DynamicURLRoute


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
        courses = app_context.db.query(Courses)

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
        if app_context.response["error"]:
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

            app_context.db.add(course)
            app_context.db.commit()

        except Exception:
            app_context.db.rollback()

            app_context.response["pop_message"] = "Course could not be created."

            return data

        result = cls.json(course)

        if result:
            result["mcq_ex"] = True

        return result

    # UPDATE

    @classmethod
    def update(cls, data):
        if app_context.response["error"]:
            return data

        item_id = data.get("id")

        if not item_id:
            item_id = app_context.function.getRequestInt("item")

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
            app_context.db.commit()

        except Exception:
            app_context.db.rollback()

            app_context.response["pop_message"] = "Course could not be updated."

            return data

        return "Update Successfully"

    # DELETE

    @classmethod
    def delete(cls, data):
        item_id = data.get("id")

        if not item_id:
            item_id = app_context.function.getRequestInt("item")

        course = cls.get(item_id, raw=True)

        if course is None:
            return "Not any query found."

        try:
            app_context.db.delete(course)
            app_context.db.commit()

        except Exception:
            app_context.db.rollback()

            app_context.response["pop_message"] = "Course could not be deleted."

            return data

        return {
            "redirect": True,
        }

    # INDEX

    @classmethod
    async def index(cls, roots: DynamicURLRoute):

        # -----------------------------------------------------
        # API POST
        # -----------------------------------------------------

        if app_context.function.is_api() and app_context.function.is_post():
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

            if app_context.response["error"]:
                return [{"error": app_context.response["error"]}]

            if callable(bind_function):
                result = bind_function(app_context.data_querys)

                return [{"bind": result}]

            return [{"error": "Session error, time out."}]

        # -----------------------------------------------------
        # ADMIN
        # -----------------------------------------------------

        app_context.response["data_querys"] = cls.get(True)

        return "admin/courses"
