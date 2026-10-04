from sqlalchemy import select

from includes.admin.modals import checked, emptyMessage
from includes.core.globals.coreutils import is_empty, slugify
from includes.core.globals.entry import app_context
from includes.core.metadata import MetaData
from includes.database.models.owner import Subject
from includes.database.models.secondary import Books
from includes.schemas.router_schema import DynamicURLRoute
from includes.utils.utils import get_post_value
from includes.database.connection import active_secondary_db


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
    async def getList(cls, limit=10):
        db = await active_secondary_db()

        books_stmt = (
            select(Books)
            .order_by(Books.id.desc())
            .limit(limit)
        )

        books = db.execute(books_stmt).scalars().all()

        subjects_stmt = select(
            Subject.id,
            Subject.name,
            Subject.slug,
        )

        subjects = {
            subject_id: {
                "id": subject_id,
                "name": name,
                "slug": slug,
            }
            for subject_id, name, slug
            in db.execute(subjects_stmt).all()
        }

        return [
            cls.json(
                item,
                subjects.get(item.subject),
            )
            for item in books
        ]

    # =========================================================
    # GET
    # =========================================================

    @classmethod
    async def get(cls, value=None, raw=False):
        if value is None:
            return None

        stmt = (
            select(Books)
            .where(
                (Books.id == value)
                | (Books.slug == value)
            )
            .limit(1)
        )
        
        db = await active_secondary_db()

        query = db.execute(stmt).scalar_one_or_none()

        return query if raw else cls.json(query)

    # =========================================================
    # INSERT
    # =========================================================

    @classmethod
    async def insert(cls, data):
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
        db = await active_secondary_db()

        try:
            book = Books(
                slug=slug,
                name=name,
                excerpt=data.get("excerpt"),
                image_src=data.get("image_src"),
                writer=int(writer) if writer else 0,
                subject=int(subject) if subject else 0,
            )

            db.add(book)
            db.commit()

        except Exception:
            db.rollback()

            app_context.response["pop_message"] = (
                "Book could not be created."
            )

            return data

        result = cls.json(book)

        if result:
            result["redirect"] = True

        return result

    # =========================================================
    # UPDATE
    # =========================================================

    @classmethod
    async def update(cls, data):
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

        db = await active_secondary_db()
        try:
            db.commit()

        except Exception:
            db.rollback()

            app_context.response["pop_message"] = (
                "Book could not be updated."
            )

            return data

        app_context.response["message"] = (
            "Updated <a href='/admin/books'>Back</a>"
        )

        return data

    # =========================================================
    # DELETE
    # =========================================================

    @classmethod
    async def delete(cls, data):
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
        db = await active_secondary_db()

        if not backup:
            app_context.response["pop_message"] = (
                "This 'books' id not delete. Error code Xe742524"
            )
            return {"redirect": True}

        try:
            db.delete(book)
            db.commit()

        except Exception:
            db.rollback()

            app_context.response["pop_message"] = (
                "This 'books' id not delete. Error code Xe742524"
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
                    app_context.response["error"] = (
                        app_context.response["error"]
                        or emptyMessage(
                            key,
                            "cls.admin.defaults,",
                        )
                    )

        if not data and not is_post:
            data = dict(zip(fields, defaults))

        return data

    # =========================================================
    # COLLECTION
    # =========================================================

    @classmethod
    async def addCollection(cls, data):
        subject_id = data.get("subject_id") or 0

        try:
            subject_id = int(subject_id)
        except (TypeError, ValueError):
            subject_id = 0

        db = await active_secondary_db()

        stmt = (
            select(
                Subject.id,
                Subject.name,
                Subject.slug,
            )
            .order_by(Subject.name)
        )

        rows = db.execute(stmt).all()

        subjects = []

        for subject_id_db, name, slug in rows:
            item = {
                "id": subject_id_db,
                "name": name,
                "slug": slug,
            }

            if subject_id_db == subject_id:
                data["subject_name"] = name

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

            bind_function = getattr(cls,roots.scope_slug,None)
            if callable(bind_function) and ( cls.function.is_post() or bind_function == cls.delete):
                result = await bind_function(cls.data_querys)

                if (isinstance(result, dict) and result.get("redirect")):
                    MetaData.redirect_url = "/admin/books"
                    return "redirect"

            app_context.response["data_querys"] = (
                cls.addCollection(cls.data_querys)
            )

            return "admin/add_books"

        app_context.response["data_querys"] = cls.getList(10)

        return "admin/books"
