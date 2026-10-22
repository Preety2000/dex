from sqlalchemy import asc

from includes.core.globals.entry import app_context
from includes.database.connection import config_secondary_db
from includes.database.dataclass.dataclass import _Article
from includes.database.models.secondary import UserRelationships


async def populate_article_likes(record: _Article) -> list[int]:
    """
    Load article likes, update the article's like count,
    and return a list of member IDs who liked the article.
    """

    db = await config_secondary_db()
    all_relationships = (
        db.query(UserRelationships)
        .filter(UserRelationships.article_id == record.id)
        .order_by(asc(UserRelationships.timestamp))
        .all()
    )

    record.likes = len(all_relationships)

    return [item.users_id for item in all_relationships]
