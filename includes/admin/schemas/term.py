from collections import defaultdict
from typing import Any, List, Optional

from includes.src.request import Request
from sqlalchemy import asc, delete, select

from includes.admin.modals import checked
from includes.admin.schemas.backup import ClassBeckup
from includes.core.globals.entry import GlobleCatch
from includes.core.globals.coreutils import is_empty, slugify

from includes.core.globals.route_context import Route
from includes.core.paginator import NewQueryPaginator
from includes.database.connection import config_primary_db, config_secondary_db
from includes.database.dataclass.dataclass import serialize
from includes.database.models.primary import Subject
from includes.database.models.secondary import Terms
from includes.schemas.cache.subject import SubjectCache
from includes.utils.utils import get_next_id, get_post_value


def empty_message(
    message: str,
    types: Optional[str] = None,
) -> str:
    return (
        f'This data cannot be {types or "save"} ' f"because <b>{message}</b> is empty."
    )


class AdminClassTerms:

    def __init__(self, request: Request = None):
        self.request = request

    @staticmethod
    async def get_all_terms_by_subject() -> List[dict[str, Any]]:
        """Fetch all subjects with their associated terms."""

        db = await config_primary_db()
        sdb = await config_secondary_db()

        # Subjects
        subjects_result = db.execute(select(Subject).order_by(Subject.name))
        subjects = subjects_result.scalars().all()

        if not subjects:
            return []

        # All terms
        terms_result = sdb.execute(select(Terms).order_by(asc(Terms.name)))

        all_terms = terms_result.scalars().all()

        # Group terms by subject_id
        terms_by_subject: dict[
            int,
            List[dict[str, Any]],
        ] = defaultdict(list)

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
                    "terms": terms_by_subject.get(
                        subject.id,
                        [],
                    ),
                }
            )

        return data

    async def getList(
        self,
        limit: int = 20,
        **more,
    ) -> List[dict[str, Any]]:

        async def add_subject(
            data_item: dict[str, Any],
        ) -> dict[str, Any]:

            data_item["subject"] = serialize(
                await SubjectCache.get_by_id(data_item["subject_id"])
            )

            return data_item

        all_query = select(Terms)

        db = await config_secondary_db()

        data = await NewQueryPaginator.paginate(
            db=db,
            limit=limit,
            types="query",
            model=Terms,
            request=self.request,
            query=all_query,
            transform=lambda item: add_subject(serialize(item)),
            **more,
        )

        return data.records

    async def insert(self, data: dict[str, Any]) -> dict[str, Any]:

        if self.request.state.response.get("error"):
            return data

        slug = slugify(data.get("slug"))

        # Check existing slug
        db = await config_secondary_db()
        stmt = select(Terms).where(Terms.slug == slug)

        result = db.execute(stmt)

        existing_term = result.scalars().first()

        if existing_term:
            self.request.state.response["error"] = (
                "This Category already exists with "
                f"the slug: [{existing_term.slug}]. "
                "Please change the slug. You can view it "
                f"<a target='_blank' "
                f"href='{existing_term.url}'>here</a>."
            )

            return data

        term = Terms(
            slug=slug,
            id=data.get(
                "id",
                get_next_id(db, Terms),
            ),
            resource=data.get(
                "resource",
                0,
            ),
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

    async def update(self, data: dict[str, Any]) -> Optional[dict[str, Any]]:

        if self.request.state.response.get("error"):
            return data

        item_id = self.request.query_params.get("item")

        terms_query = None

        db = await config_secondary_db()
        if item_id:
            stmt = select(Terms).where(Terms.id == int(item_id))

            result = db.execute(stmt)

            terms_query = result.scalars().first()

        if not terms_query:
            self.request.state.response["error"] = "No query record found."

            return None

        terms_query.slug = data.get(
            "slug",
            terms_query.slug,
        )

        terms_query.name = data.get(
            "name",
            terms_query.name,
        )

        terms_query.topic = data.get(
            "topic",
            terms_query.topic,
        )

        terms_query.resource = data.get(
            "resource",
            terms_query.resource,
        )

        terms_query.subject_id = data.get(
            "subject_id",
            terms_query.subject_id,
        )

        terms_query.image_src = data.get(
            "image_src",
            terms_query.image_src,
        )

        terms_query.description = data.get(
            "description",
            terms_query.description,
        )

        db.commit()

        self.request.state.response["message"] = (
            "Updated " "<a href='/admin/category'>Back</a>"
        )

        return data

    async def delete(self, id: int) -> Optional[bool]:

        terms_query = None

        db = await config_secondary_db()
        if id:
            stmt = select(Terms).where(Terms.id == id)

            result = db.execute(stmt)

            terms_query = result.scalars().first()

        if terms_query:

            if await ClassBeckup.insert(
                serialize(terms_query),
                "terms",
            ):

                # Delete main Terms record
                db.execute(delete(Terms).where(Terms.id == terms_query.id))

                # Delete related records
                db.execute(delete(Terms).where(Terms.terms_id == terms_query.id))

                db.commit()

                GlobleCatch.get_with_terms = None

                return True

            self.request.state.response["pop_message"] = {
                "title": (
                    "This 'terms' id could not be " "deleted. Error code Xe742524"
                ),
                "url": "/admin/category",
            }

            return None

        self.request.state.response["pop_message"] = {
            "title": ("This 'terms' id was not found. " "Error code Xe742525"),
            "url": "/admin/category",
        }

        return None

    async def terms_query(self, roots: Route) -> dict[str, Any]:
        async def add_more(term: dict[str, Any]) -> dict[str, Any]:

            self.request.state.response["subjects"] = []
            subject_id = int(term.get("subject_id") or 0)

            for subject in await SubjectCache.get_all():

                item = serialize(subject)

                if checked(
                    subject.id == subject_id,
                    item,
                ):
                    term["subject_name"] = subject.name

                self.request.state.response["subjects"].append(item)

            topic_enabled = int(term.get("topic") or 0) == 1

            resource_enabled = int(term.get("resource") or 0) == 1

            term.update(
                {
                    "topic_name": ("Enable" if topic_enabled else "Disable"),
                    "topic_enable": ("checked" if topic_enabled else None),
                    "topic_desable": (None if topic_enabled else "checked"),
                    "resource_name": ("Enable" if resource_enabled else "Disable"),
                    "resource_enable": ("checked" if resource_enabled else None),
                    "resource_desable": (None if resource_enabled else "checked"),
                }
            )

            return term

        db = await config_secondary_db()

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

        # POST
        if self.request.is_post:

            terms_query_data = await get_post_value(
                self.request,
                query_terms_keys,
                query_terms_defaults,
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
                    self.request.state.response[
                        "error"
                    ] = self.request.state.response.get("error") or empty_message(
                        key,
                        roots.scope,
                    )

            return await add_more(terms_query_data)

        # GET / Update
        item_id = self.request.query_params.get("item")

        terms_query_data = None

        if item_id:
            db = await config_secondary_db()
            stmt = select(Terms).where(Terms.id == int(item_id))

            result = db.execute(stmt)

            record = result.scalars().first()

            terms_query_data = serialize(record) if record else None

        if not terms_query_data:
            terms_query_data = {
                key.replace("[]", ""): query_terms_defaults[i]
                for i, key in enumerate(query_terms_keys)
            }

        return await add_more(terms_query_data)

    async def index(self, roots: Route) -> str:

        if roots.scope == "delete" and await self.delete(
            self.request.query_params.get("item")
        ):
            self.request.state.metadata.redirect_url = "/admin/category"

            return "redirect"

        if roots.scope in ("insert", "update"):
            data_querys = await self.terms_query(roots)
            bind_function = getattr(self, roots.scope, None)
            if self.request.is_post and callable(bind_function):
                bind_value = await bind_function(data_querys)

                if bind_value and bind_value.get("redirect"):
                    self.request.state.metadata.redirect_url = "/admin/category"

                    return "redirect"

            self.request.state.response["data_querys"] = data_querys

            return "admin/add_terms"

        self.request.state.response["data_querys"] = await self.getList(10)

        return "admin/terms"
