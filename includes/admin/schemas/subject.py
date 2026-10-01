from includes.core.globals.entry import app_context
from includes.db.models.owner import Subject
from includes.schemas.cache.subject import SubjectCache


class AdminSubject:

    @classmethod
    async def get_all_subject(cls):
        return [
            SubjectCache._cache(record.to_dataclass())
            for record in app_context.db.query(Subject).order_by(Subject.name).all()
        ]
