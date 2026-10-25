from sqlalchemy import select

from includes.admin.modals import emptyMessage
from includes.core.globals.coreutils import is_empty, slugify
from includes.core.globals.entry import app_context
from includes.core.globals.route_context import Route
from includes.database.models.primary import Subject
from includes.database.models.secondary import Books
from includes.utils.utils import get_post_value
from includes.database.connection import config_primary_db, config_secondary_db


class ClassBooks:

    def __init__(self, request):
        self.request = request

    # =========================================================
    # HELPERS
    # =========================================================

    def get_item_id(self):
        """Get item ID from the request safely."""
        try:
            value = self.request.query_params.get("item")
            return int(value) if value else None
        except (AttributeError, TypeError, ValueError):
            return None

    @staticmethod
    def to_int(value, default=0):
        try:
            return int(value) if value not in (None, "") else default
        except (TypeError, ValueError):
            return default

    # =========================================================
    # JSON
    # =========================================================

    def json(self, query, subject=None):
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

    async def getList(self, limit=10):
        dbp = await config_primary_db()
        db = await config_secondary_db()

        try:
            books_stmt = select(Books).order_by(Books.id.desc()).limit(limit)

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
                for subject_id, name, slug in dbp.execute(subjects_stmt).all()
            }

            return [self.json(item, subjects.get(item.subject)) for item in books]

        except Exception:
            raise

    # =========================================================
    # GET
    # =========================================================

    async def get(self, value=None, raw=False):
        if value is None or value == "":
            return None

        db = await config_secondary_db()

        try:
            conditions = [Books.slug == str(value)]

            item_id = self.to_int(value, default=None)

            if item_id is not None:
                conditions.append(Books.id == item_id)

            stmt = select(Books).where(*[conditions[0]]).limit(1)

            # Match either the numeric ID or the slug.
            from sqlalchemy import or_

            stmt = select(Books).where(or_(*conditions)).limit(1)

            query = db.execute(stmt).scalar_one_or_none()

            return query if raw else self.json(query)

        except Exception:
            raise

    # =========================================================
    # INSERT
    # =========================================================

    async def insert(self, data):
        if self.request.state.response.get("error"):
            return data

        name = data.get("name")

        if not name:
            return data

        slug = slugify(data.get("slug") or name)

        db = await config_secondary_db()

        try:
            # Check for duplicate slug.
            stmt = select(Books).where(Books.slug == slug).limit(1)
            existing = db.execute(stmt).scalar_one_or_none()

            if existing:
                result = self.json(existing)
                result["redirect"] = True
                return result

            writer = self.to_int(data.get("writer_id"))
            subject = self.to_int(data.get("subject_id"))

            book = Books(
                slug=slug,
                name=name,
                excerpt=data.get("excerpt"),
                image_src=data.get("image_src"),
                writer=writer,
                subject=subject,
            )

            db.add(book)
            db.commit()
            db.refresh(book)

            result = self.json(book)
            result["redirect"] = True

            return result

        except Exception:
            db.rollback()

            self.request.state.response["pop_message"] = "Book could not be created."

            return data

    # =========================================================
    # UPDATE
    # =========================================================

    async def update(self, data):
        if self.request.state.response.get("error"):
            return data

        item_id = data.get("id") or self.get_item_id()

        if not item_id:
            self.request.state.response["error"] = "Book ID is required."
            return data

        db = await config_secondary_db()

        try:
            item_id = self.to_int(item_id, default=None)

            if item_id is None:
                self.request.state.response["error"] = "Invalid book ID."
                return data

            stmt = select(Books).where(Books.id == item_id).limit(1)
            book = db.execute(stmt).scalar_one_or_none()

            if book is None:
                self.request.state.response["error"] = "No book found."
                return data

            # Update slug and check for duplicates.
            if data.get("slug"):
                new_slug = slugify(data["slug"])

                duplicate_stmt = (
                    select(Books)
                    .where(
                        Books.slug == new_slug,
                        Books.id != book.id,
                    )
                    .limit(1)
                )

                duplicate = db.execute(duplicate_stmt).scalar_one_or_none()

                if duplicate:
                    self.request.state.response["pop_message"] = (
                        "This slug is already in use."
                    )
                    return data

                book.slug = new_slug

            if data.get("name") is not None:
                book.name = data["name"]

            if data.get("writer_id") is not None:
                book.writer = self.to_int(data["writer_id"])

            if data.get("subject_id") is not None:
                book.subject = self.to_int(data["subject_id"])

            if data.get("excerpt") is not None:
                book.excerpt = data["excerpt"]

            if data.get("image_src") is not None:
                book.image_src = data["image_src"]

            db.commit()

            self.request.state.response["message"] = (
                "Updated <a href='/admin/books'>Back</a>"
            )

            return data

        except Exception:
            db.rollback()

            self.request.state.response["pop_message"] = "Book could not be updated."

            return data

    # =========================================================
    # DELETE
    # =========================================================

    async def delete(self, data):
        item_id = data.get("id") or self.get_item_id()

        if not item_id:
            self.request.state.response["pop_message"] = "Book ID is required."
            return {"redirect": True}

        db = await config_secondary_db()

        try:
            item_id = self.to_int(item_id, default=None)

            if item_id is None:
                self.request.state.response["pop_message"] = "Invalid book ID."
                return {"redirect": True}

            stmt = select(Books).where(Books.id == item_id).limit(1)
            book = db.execute(stmt).scalar_one_or_none()

            if book is None:
                self.request.state.response["pop_message"] = "Book not found."
                return {"redirect": True}

            book_json = self.json(book)

            # Add your backup operation here if required.
            # Example:
            # backup = await self.admin.backup.insert(
            #     book_json, "books"
            # )

            db.delete(book)
            db.commit()

            book_json["redirect"] = True
            return book_json

        except Exception:
            db.rollback()

            self.request.state.response["pop_message"] = (
                "Book could not be deleted. Error code Xe742524"
            )

            return {"redirect": True}

    # =========================================================
    # FORM DATA
    # =========================================================

    async def getCollection(self):
        item_id = self.get_item_id()
        is_post = self.request.is_post

        data = await self.get(item_id)

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
            "empty.webp",
        ]

        if is_post:
            data = await get_post_value(
                self.request,
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
                    self.request.state.response["error"] = (
                        self.request.state.response.get("error")
                        or emptyMessage(key, "self.admin.defaults,")
                    )

        elif not data:
            data = dict(zip(fields, defaults))

        return data

    # =========================================================
    # COLLECTION
    # =========================================================

    async def addCollection(self, data):
        selected_subject_id = self.to_int(data.get("subject_id"))

        db = await config_primary_db()

        stmt = select(
            Subject.id,
            Subject.name,
            Subject.slug,
        ).order_by(Subject.name)

        rows = db.execute(stmt).all()
        subjects = []

        for subject_id_db, name, slug in rows:
            item = {
                "id": subject_id_db,
                "name": name,
                "slug": slug,
            }

            if subject_id_db == selected_subject_id:
                data["subject_name"] = name

            subjects.append(item)

        app_context.params.subjects = subjects

        return data

    # =========================================================
    # INDEX
    # =========================================================

    async def index(self, roots: Route):
        if roots.scope in ("insert", "update", "delete"):
            self.data_querys = await self.getCollection()

            bind_function = getattr(self, roots.scope, None)

            should_execute = callable(bind_function) and (
                self.request.is_post or roots.scope == "delete"
            )

            if should_execute:
                result = await bind_function(self.data_querys)

                if isinstance(result, dict) and result.get("redirect"):
                    self.request.state.metadata.redirect_url = "/admin/books"
                    return "redirect"

            self.request.state.response["data_querys"] = await self.addCollection(
                self.data_querys
            )

            return "admin/add_books"

        self.request.state.response["data_querys"] = await self.getList(10)

        return "admin/books"
