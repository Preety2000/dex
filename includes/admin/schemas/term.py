from collections import defaultdict
from typing import Any, List, Optional

from includes.admin.modals import checked
from includes.admin.schemas.backup import ClassBeckup
from includes.core.globals.coreutils import is_empty, slugify
from includes.core.globals.entry import GlobleCatch, app_context
from includes.core.metadata import MetaData
from includes.core.paginator import NewQueryPaginator
from includes.db.connection import active_secondary_db
from includes.db.dataclass import serialize
from includes.db.models.owner import Subject
from includes.db.models.secondary import Terms
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.router_schema import DynamicURLRoute
from includes.utils.utils import get_next_id, get_post_value
from sqlalchemy import asc, desc, select


def empty_message(message: str, types: Optional[str] = None) -> str:
    return f'This data cannot be {types or "save"} because <b>{message}</b> is empty.'


class AdminClassTerms:

    @staticmethod
    async def get_all_terms_by_subject() -> List[dict[str, Any]]:
        """Fetch all subjects with their associated terms.

        Optimized to prevent N+1 queries.
        """
        db, sdb = await app_context.db.configure()

        subjects = db.query(Subject).order_by(Subject.name).all()
        if not subjects:
            return []

        # Optimization: Fetch all terms in a single query instead of executing inside the loop
        all_terms = sdb.query(Terms).order_by(asc(Terms.name)).all()

        # Group terms by subject_id
        terms_by_subject: dict[int, List[dict[str, Any]]] = defaultdict(list)
        for term in all_terms:
            terms_by_subject[term.subject_id].append(
                {
                    "id": term.id,
                    "name": term.name,
                    "slug": term.slug,
                    "subject_id": term.subject_id,
                }
            )

        data = []
        for record in subjects:
            subject = SubjectCache._cache(record.to_dataclass())
            data.append(
                {
                    "id": subject.id,
                    "name": subject.name,
                    "slug": subject.slug,
                    "terms": terms_by_subject.get(subject.id, []),
                }
            )

        return data

    @staticmethod
    async def getList(limit: int = 20, **more) -> List[dict[str, Any]]:
        """Fetch paginated terms records with subject metadata attached."""

        async def add_subject(data_item: dict[str, Any]) -> dict[str, Any]:
            data_item["subject"] = serialize(
                await SubjectCache.get_by_id(data_item["subject_id"])
            )
            return data_item

        all_query = select(Terms)
        db = await active_secondary_db()
        data = await NewQueryPaginator.paginate(
            db=db,
            limit=limit,
            types="query",
            model=Terms,
            query=all_query,
            transform=lambda item: add_subject(serialize(item)),
            **more,
        )
        return data.records

    @staticmethod
    async def insert(data: dict[str, Any]) -> dict[str, Any]:
        if app_context.response.get("error"):
            return data

        slug = slugify(data.get("slug"))
        existing_term = app_context.db.query(Terms).filter(Terms.slug == slug).first()

        if existing_term:
            app_context.response["error"] = (
                f"This Category already exists with the slug: [{existing_term.slug}]. "
                f"Please change the slug. You can view it <a target='_blank' href='{existing_term.url}'>here</a>."
            )
            return data

        _, db = await app_context.db.configure()

        term = Terms(
            slug=slug,
            id=data.get("id", get_next_id(db, Terms)),
            resource=data.get("resource", 0),
            name=data.get("name"),
            image_src=data.get("image_src"),
            topic=int(data.get("topic", 0)),
            subject_id=int(data.get("subject_id")),
            description=data.get("description"),
            used=int(data.get("used", 0)),
        )

        db.add(term)
        db.commit()

        return {"redirect": True}

    @staticmethod
    async def update(data: dict[str, Any]) -> Optional[dict[str, Any]]:
        if app_context.response.get("error"):
            return data

        item_id = app_context.function.getRequestInt("item")
        terms_query = (
            app_context.db.query(Terms).filter(Terms.id == int(item_id)).first()
            if item_id
            else None
        )

        if not terms_query:
            app_context.response["error"] = "No query record found."
            return None

        terms_query.slug = data.get("slug", terms_query.slug)
        terms_query.name = data.get("name", terms_query.name)
        terms_query.topic = data.get("topic", terms_query.topic)
        terms_query.resource = data.get("resource", terms_query.resource)
        terms_query.subject_id = data.get("subject_id", terms_query.subject_id)
        terms_query.image_src = data.get("image_src", terms_query.image_src)
        terms_query.description = data.get("description", terms_query.description)

        app_context.db.commit()
        app_context.response["message"] = "Updated <a href='/admin/category'>Back</a>"
        return data

    @staticmethod
    async def delete(id: int) -> Optional[bool]:
        terms_query = (
            app_context.db.query(Terms).filter(Terms.id == id).first() if id else None
        )

        if terms_query:
            if await ClassBeckup.insert(serialize(terms_query), "terms"):
                app_context.db.query(Terms).filter_by(id=terms_query.id).delete()
                app_context.db.query(Terms).filter_by(terms_id=terms_query.id).delete()
                app_context.db.commit()
                GlobleCatch.get_with_terms = None
                return True

            app_context.response["pop_message"] = {
                "title": "This 'terms' id could not be deleted. Error code Xe742524",
                "url": "/admin/category",
            }
            return None

        app_context.response["pop_message"] = {
            "title": "This 'terms' id was not found. Error code Xe742525",
            "url": "/admin/category",
        }
        return None

    @staticmethod
    async def terms_query(roots: DynamicURLRoute) -> dict[str, Any]:

        async def add_more(term: dict[str, Any]) -> dict[str, Any]:
            app_context.response["subjects"] = []
            subject_id = int(term.get("subject_id") or 0)

            for subject in await SubjectCache.get_all():
                item = serialize(subject)
                if checked(subject.id == subject_id, item):
                    term["subject_name"] = subject.name

                app_context.response["subjects"].append(item)

            topic_enabled = int(term.get("topic") or 0) == 1
            resource_enabled = int(term.get("resource") or 0) == 1

            term.update(
                {
                    "topic_name": "Enable" if topic_enabled else "Disable",
                    "topic_enable": "checked" if topic_enabled else None,
                    "topic_desable": None if topic_enabled else "checked",
                    "resource_name": "Enable" if resource_enabled else "Disable",
                    "resource_enable": "checked" if resource_enabled else None,
                    "resource_desable": None if resource_enabled else "checked",
                }
            )

            return term

        _, db = await app_context.db.configure()
        query_terms_keys = [
            "id",
            "name",
            "slug",
            "resource",
            "topic",
            "subject_id",
            "image_src",
            "description",
        ]
        query_terms_defaults = [
            get_next_id(db, Terms),
            "",
            "",
            "",
            "",
            0,
            "",
            "",
        ]

        if app_context.function.is_post():
            terms_query_data = await get_post_value(
                query_terms_keys, query_terms_defaults
            )

            slug = terms_query_data["slug"].strip()
            if not slug:
                slug = terms_query_data["name"].strip()

            terms_query_data.update({"slug": slugify(slug)})

            for key, value in terms_query_data.items():
                if is_empty(value) and key not in [
                    "description",
                    "image_src",
                ]:
                    app_context.response["error"] = app_context.response.get(
                        "error"
                    ) or empty_message(key, roots.scope_slug)

            return await add_more(terms_query_data)

        item_id = app_context.function.getRequestInt("item")
        terms_query_data = serialize(
            app_context.db.query(Terms).filter(Terms.id == int(item_id)).first()
            if item_id
            else None
        )

        if not terms_query_data:
            terms_query_data = {
                key.replace("[]", ""): query_terms_defaults[i]
                for i, key in enumerate(query_terms_keys)
            }

        return await add_more(terms_query_data)

    @staticmethod
    async def index(roots: DynamicURLRoute) -> str:
        if roots.scope_slug == "delete" and await AdminClassTerms.delete(
            app_context.function.getRequestInt("item")
        ):
            MetaData.redirect_url = "/admin/category"
            return "redirect"

        if roots.scope_slug in ("insert", "update"):
            data_querys = await AdminClassTerms.terms_query(roots)
            bind_function = getattr(AdminClassTerms, roots.scope_slug, None)

            if app_context.function.is_post() and callable(bind_function):
                bind_value = await bind_function(data_querys)

                if bind_value and bind_value.get("redirect"):
                    MetaData.redirect_url = "/admin/category"
                    return "redirect"

            app_context.response["data_querys"] = data_querys
            return "admin/add_terms"

        app_context.response["data_querys"] = await AdminClassTerms.getList(10)
        return "admin/terms"


# Alias for backward compatibility
AsminClassTerms = AdminClassTerms
