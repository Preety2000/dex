from sqlalchemy import select

from includes.core.paginator import NewQueryPaginator
from includes.database.connection import active_secondary_db
from includes.utils._sub import configure_page
from includes.core.globals.entry import app_context
from includes.database.models.secondary import Syllabus
from includes.schemas.subject import ClassSubject
from includes.schemas.university import ClassUniversity


class ClassSyllabus:

    @staticmethod
    def json(query, quet=None):
        if not query:
            return None

        ClassUniversity.add_syllabus = False
        is_university = ClassUniversity.get(query.university, True)

        subject = ClassSubject.get(query.subject) if quet is True else query.subject
        university = (
            ClassUniversity.get(query.university) if quet is True else query.university
        )
        return {
            "id": query.id,
            "slug": query.slug,
            "url": app_context.request.host_url
            + "syllabus/"
            + is_university.slug
            + "/"
            + query.slug,
            "title": query.title,
            "content": query.content,
            "subject": subject,
            "university": university,
            "timestamp": query.timestamp,
        }

    @classmethod
    async def get(cls, query=None, **more):

        syllabus = select(Syllabus)

        db = await active_secondary_db()

        # If no query, return all syllabuses
        if query is True and isinstance(query, bool):
            data = await NewQueryPaginator.paginate(
                db=db,
                types="query",
                model=Syllabus,
                query=syllabus,
                transform=lambda item: cls.json(item, True),
                **more
            )

            return data.records

        # Try filtering by id, slug, or title, returning the first match
        syllabus_query = syllabus.filter(
            (Syllabus.id == query) | (Syllabus.slug == query)
        ).first()

        return cls.json(syllabus_query, True)

    @classmethod
    async def index(cls, subresource, detail):

        if not subresource:
            ClassUniversity.add_syllabus = True
            university = ClassUniversity.get(True)
            configure_page(title="Syllabus", suffix=True)

            app_context.response["data_querys"] = university
            return "widget/syllabus"

        if detail:
            syllabus = await cls.get(detail)
            configure_page(title=syllabus.get("title"))
            app_context.response["data_querys"] = syllabus
            return "query/syllabus_view"

        return "error.html"
