from sqlalchemy import asc
from includes.core.globals.entry import app_context
from includes.database.models.secondary import Courses, Syllabus, University


class ClassUniversity:

    @staticmethod
    def property(query):
        query.syllabus = app_context.db.query(Syllabus).filter(
            Syllabus.university == query.id
        )
        query.courses = app_context.db.query(Courses).filter(
            Courses.university == query.id
        )
        return query

    @classmethod
    def json(cls, query):
        if not query:
            return None
        query = cls.property(query)

        university_query = {"id": query.id, "slug": query.slug, "name": query.name}

        return university_query

    @classmethod
    def get(cls, query=None, quet=None):
        university = app_context.db.query(University)

        if query is True and isinstance(query, bool):
            all_university = university.order_by(asc(University.name)).all()
            return [cls.json(item) for item in all_university]

        university_query = university.filter(
            (University.id == query)
            | (University.slug == query)
            | (University.name == query)
        ).first()

        return cls.json(university_query) if quet is None else university_query
