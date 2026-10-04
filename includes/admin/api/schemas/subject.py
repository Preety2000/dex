from includes.core.globals.entry import app_context
from includes.database.connection import active_primary_db
from includes.database.dataclass.dataclass import serialize
from includes.database.models.owner import Subject
from includes.schemas.cache.subject import SubjectCache
from includes.utils.utils import (
    create_slug,
    get_next_id,
    get_post_value,
)


class AdminApiSubject:

    @staticmethod
    async def insert():

        data = {
            field: await get_post_value(field) for field in ("name", "content", "slug")
        }

        name = (data.get("name") or "").strip()

        if not name:
            return {"error": "Subject Name is required."}

        db = await active_primary_db()

        slug = create_slug((data.get("slug") or name).strip())
        existing = db.query(Subject).filter(Subject.slug == slug).first()

        if existing:

            return {
                "error": (
                    "This Subject already exists with "
                    f"the slug <strong>{existing.slug}</strong>. "
                    "Please choose a different slug. "
                    f'<a target="_blank" '
                    f'href="/admin/subject/update?item={existing.id}">'
                    "View Subject"
                    "</a>."
                )
            }

        subject_id = get_next_id(
            db,
            Subject,
        )

        subject = Subject(
            id=subject_id, slug=slug, name=name, content=data.get("content")
        )

        try:

            db.add(subject)
            db.commit()
            SubjectCache._cache(subject.to_dataclass())

            return {
                "success": True,
                "message": ("Subject created successfully."),
                "data": serialize(subject),
            }

        except Exception:

            db.rollback()
            raise

    @classmethod
    async def execute(
        cls,
        root_name: str | None = None,
    ):

        if root_name == "insert":
            return await cls.insert()

        return []
