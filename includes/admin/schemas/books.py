from includes.admin.modals import checked, emptyMessage
from includes.core.globals.coreutils import is_empty, slugify
from includes.core.globals.entry import app_context
from includes.core.metadata import MetaData
from includes.db.models.owner import Subject
from includes.db.models.secondary import Books
from includes.schemas.router_schema import DynamicURLRoute
from includes.utils.utils import get_post_value


class ClassBooks:

    # =========================================================
    # JSON
    # =========================================================

    @classmethod
    def json(cls, query, subject=None):
        if query is None:
            return None

        data = {
            "id": query.id,
            "slug": query.slug,
            "name": query.name,
            "excerpt": query.excerpt,
            "subject": query.subject,
            "writer": query.writer,
            "image_src": query.image_src,
        }

        if subject:
            for name, value in subject.items():
                data[f"subject_{name}"] = value

        return data

    # =========================================================
    # GET LIST
    # =========================================================

    @classmethod
    def getList(cls, limit=10):
        query = app_context.db.query(Books)

        subjects = {
            subject.id: {
                "id": subject.id,
                "name": subject.name,
                "slug": subject.slug,
            }
            for subject in app_context.db.query(Subject).all()
        }

        return [
            cls.json(
                item,
                subjects.get(item.subject),
            )
            for item in query
        ]

    # =========================================================
    # GET
    # =========================================================

    @classmethod
    def get(cls, value=None, raw=False):
        if value is None:
            return None

        query = (
            app_context.db.query(Books)
            .filter((Books.id == value) | (Books.slug == value))
            .first()
        )

        return query if raw else cls.json(query)

    # =========================================================
    # INSERT
    # =========================================================

    @classmethod
    def insert(cls, data):
        if app_context.response["error"]:
            return data

        name = data.get("name")
        slug = data.get("slug") or name

        if not name:
            return data

        slug = slugify(slug)

        # Duplicate slug
        if cls.get(slug, raw=True):
            result = cls.get(slug)

            if result:
                result["redirect"] = True

            return result or data

        writer = data.get("writer_id")
        subject = data.get("subject_id")

        try:
            book = Books(
                slug=slug,
                name=name,
                excerpt=data.get("excerpt"),
                image_src=data.get("image_src"),
                writer=int(writer) if writer else 0,
                subject=int(subject) if subject else 0,
            )

            app_context.db.add(book)
            app_context.db.commit()

        except Exception:
            app_context.db.rollback()

            app_context.response["pop_message"] = "Book could not be created."

            return data

        result = cls.json(book)

        if result:
            result["redirect"] = True

        return result

    # =========================================================
    # UPDATE
    # =========================================================

    @classmethod
    def update(cls, data):
        if app_context.response["error"]:
            return data

        item_id = data.get("id")

        if not item_id:
            item_id = cls.function.getRequestInt("item")

        book = cls.get(item_id, raw=True)

        if book is None:
            app_context.response["error"] = "Not any query found."
            return data

        if data.get("slug"):
            book.slug = slugify(data["slug"])

        if data.get("name") is not None:
            book.name = data["name"]

        if data.get("writer_id") is not None:
            try:
                book.writer = int(data["writer_id"])
            except (TypeError, ValueError):
                pass

        if data.get("subject_id") is not None:
            try:
                book.subject = int(data["subject_id"])
            except (TypeError, ValueError):
                pass

        if data.get("excerpt") is not None:
            book.excerpt = data["excerpt"]

        if data.get("image_src") is not None:
            book.image_src = data["image_src"]

        try:
            app_context.db.commit()

        except Exception:
            app_context.db.rollback()

            app_context.response["pop_message"] = "Book could not be updated."

            return data

        app_context.response["message"] = "Updated <a href='/admin/books'>Back</a>"

        return data

    # =========================================================
    # DELETE
    # =========================================================

    @classmethod
    def delete(cls, data):
        item_id = data.get("id")

        if not item_id:
            item_id = cls.function.getRequestInt("item")

        book = cls.get(item_id, raw=True)

        if book is None:
            app_context.response["pop_message"] = "Book not found."
            return {"redirect": True}

        book_json = cls.json(book)

        # Backup
        # backup = cls.admin.backup.insert(
        #     book_json,
        #     "books",
        # )

        backup = None

        if not backup:
            app_context.response["pop_message"] = (
                "This 'books' id not delete. " "Error code Xe742524"
            )
            return {"redirect": True}

        try:
            app_context.db.delete(book)
            app_context.db.commit()

        except Exception:
            app_context.db.rollback()

            app_context.response["pop_message"] = (
                "This 'books' id not delete. " "Error code Xe742524"
            )

            return {"redirect": True}

        book_json["redirect"] = True

        return book_json

    # =========================================================
    # FORM DATA
    # =========================================================

    @classmethod
    async def getCollection(cls):
        item_id = cls.function.getRequestInt("item")
        is_post = cls.function.is_post()

        data = cls.get(item_id)

        fields = [
            "name",
            "slug",
            "excerpt",
            "writer_id",
            "subject_id",
            "image_src",
        ]

        defaults = [
            "",
            "",
            "",
            0,
            0,
            "empty.png",
        ]

        if is_post:
            data = await get_post_value(
                fields,
                defaults,
            )

            slug = data.get("slug")

            if is_empty(slug):
                slug = data.get("name")

            if slug:
                data["slug"] = slugify(slug)

            for key, value in data.items():
                if is_empty(value) and key != "excerpt":
                    app_context.response["error"] = app_context.response[
                        "error"
                    ] or emptyMessage(key, "cls.admin.defaults,")

        if not data and not is_post:
            data = dict(zip(fields, defaults))

        return data

    # =========================================================
    # COLLECTION
    # =========================================================

    @classmethod
    def addCollection(cls, data):
        subject_id = data.get("subject_id") or 0

        try:
            subject_id = int(subject_id)
        except (TypeError, ValueError):
            subject_id = 0

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

        app_context.params.subjects = subjects

        return data

    # =========================================================
    # INDEX
    # =========================================================

    @classmethod
    async def index(cls, roots: DynamicURLRoute):

        if roots.scope_slug in (
            "insert",
            "update",
            "delete",
        ):
            cls.data_querys = await cls.getCollection()

            bind_function = getattr(cls, roots.scope_slug, None)

            if callable(bind_function) and (
                cls.function.is_post() or bind_function == cls.delete
            ):
                result = bind_function(cls.data_querys)

                if isinstance(result, dict) and result.get("redirect"):
                    MetaData.redirect_url = "/admin/books"
                    return "redirect"

            app_context.response["data_querys"] = cls.addCollection(cls.data_querys)

            return "admin/add_books"

        app_context.response["data_querys"] = cls.getList(10)

        return "admin/books"
