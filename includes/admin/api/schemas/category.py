from includes.core.globals.entry import app_context
from includes.db.models.owner import Subject
from includes.db.models.secondary import Terms
from includes.schemas.cache.terms import TermsCache, TermsCacheData
from includes.utils.utils import create_slug, get_next_id, get_post_value


class AdminApiCategory:

    @classmethod
    async def insert(cls):
        replace = await get_post_value("replace")
        fields = ["description", "name", "resource", "slug", "subject", "topic"]
        data = {i: await get_post_value(i) for i in fields}

        if not data["name"] or not data["subject"] or not data["description"]:
            return {"error": "Category name, description and subject are required."}

        msb, db = await app_context.db.configure()

        slug = create_slug(data.get("slug") or data["name"])

        subject = msb.query(Subject).filter(Subject.name == data["subject"]).first()
        if subject is None:
            return {"error": "6a8473f9-73d4-83ea-ba81-6a76a0d9fd8"}

        existing = (
            app_context.db.query(Terms)
            .filter(
                Terms.slug == slug,
                Terms.name == data["name"],
            )
            .first()
        )

        if existing and replace:
            existing.slug = (slug,)
            existing.name = (data["name"],)
            existing.subject_id = (subject.id,)
            existing.resource = (int(data.get("resource") or 0),)
            existing.topic = (int(data.get("topic") or 0),)
            existing.description = data["description"]
            db.commit()
            try:
                TermsCache._cache(existing)
            except:
                TermsCache._cache_remove()

            return {"replace": True}

        if existing:

            return {
                "error": (
                    f"This category already exists with the slug "
                    f"<strong>{existing.slug}</strong>. "
                    f"Please choose a different slug. "
                    f"<a target='_blank' href='{existing.url}'>View category</a>."
                )
            }

        tid = get_next_id(db, Terms)

        term = Terms(
            id=tid,
            slug=slug,
            name=data["name"],
            subject_id=subject.id,
            resource=int(data.get("resource") or 0),
            topic=int(data.get("topic") or 0),
            description=data["description"],
        )

        try:
            db.add(term)
            db.commit()

            TermsCacheData.allList = None
            try:
                TermsCache._cache(term)
            except:
                TermsCache._cache_remove()

            return {
                "success": True,
                "message": "Category created successfully.",
                "data": {
                    "id": tid,
                    "slug": slug,
                    "name": data["name"],
                    "topic": data["topic"],
                    "subject_id": subject.id,
                    "resource": data["resource"],
                },
            }

        except Exception:
            db.rollback()
            raise

    @classmethod
    async def execute(cls, root_name: str = None):

        if root_name == "insert":
            return await cls.insert()

        return []
