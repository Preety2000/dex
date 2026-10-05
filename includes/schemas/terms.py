from includes.core.globals.entry import app_context
from includes.core.globals.coreutils import matches_filters
from includes.database.dataclass.dataclass import serialize
from includes.database.models.secondary import (
    Article,
    QuizQuestion,
    QuizRelationships,
    Terms,
    TermsRelationship,
)
from includes.schemas.cache.terms import TermsCache
from includes.schemas.objective import get_mini_mcq_json
from includes.utils.arti import get_mini_article_json


def get_terms_json(item):
    if not item:
        return item

    image_src = item.image_src
    return dict(
        {
            **{c.name: getattr(item, c.name) for c in item.__table__.columns},
            "img": (
                image_src if "/" in image_src else f"/media/img/category/{image_src}"
            ),
            "url": f"{app_context.request.host_url}questions/tagged/{item.slug}",
        }
    )


class ClassTerms:

    @staticmethod
    def get(**filters):
        terms = app_context.db.query(Terms)

        for key, value in filters.items():
            if hasattr(Terms, key) and value is not None:
                terms = terms.filter(getattr(Terms, key) == value)

        query = terms.first()

        return get_terms_json(query)

    @staticmethod
    async def get_all_record(*, limit=None, bind=None, **filters):
        result = []
        for record in await TermsCache.get_all():
            if not matches_filters(record, filters):
                continue

            if callable(bind) and not bind(record):
                continue

            result.append(record)

            if limit is not None and len(result) >= limit:
                break

        return result

    @staticmethod
    async def get_all(*, limit=None, **filters):
        grouped = []

        terms_query = app_context.db.query(Terms)
        # dynamic filters
        for key, value in filters.items():
            if hasattr(Terms, key) and value is not None:
                terms_query = terms_query.filter(getattr(Terms, key) == value)

        if limit:
            all_query = terms_query.limit(limit).all()
        else:
            all_query = terms_query.all()

        for terms in all_query:
            term_data = serialize(terms)
            mcq_qs = (
                app_context.db.query(QuizQuestion)
                .join(QuizRelationships, QuizRelationships.quiz_id == QuizQuestion.id)
                .filter(QuizRelationships.terms_id == terms.id)
            )
            article_qs = (
                app_context.db.query(Article)
                .join(TermsRelationship, TermsRelationship.article_id == Article.id)
                .filter(TermsRelationship.terms_id == terms.id)
            )
            term_data.update(
                {
                    "mcq_first": await get_mini_mcq_json(mcq_qs.first()),
                    "article_first": await get_mini_article_json(article_qs.first()),
                }
            )
            grouped.append(term_data)
        return grouped
