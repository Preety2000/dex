from typing import Optional

from sqlalchemy import func, select

from includes.core.globals.fun import random_string
from includes.utils.utils import json_response
from includes.core.security import _Security
from includes.database.connection import active_secondary_db
from includes.database.models.secondary import UserRelationships

LikesCached: set[tuple[int, int]] = set()


class Likes:

    @classmethod
    def with_cache(cls, record):
        LikesCached.add((record.users_id, record.article_id))
        return record

    @classmethod
    async def get(cls, article_id: int, users_id: int) -> Optional[UserRelationships]:
        key = (users_id, article_id)

        if key in LikesCached:
            return True

        db = await active_secondary_db()

        stmt = select(UserRelationships).where(
            UserRelationships.users_id == users_id,
            UserRelationships.article_id == article_id,
        )

        record = db.execute(stmt).scalar_one_or_none()

        if record:
            cls.with_cache(record)

        return record

    @classmethod
    async def insert(cls, article_id: int, users_id: int) -> UserRelationships:
        if await cls.get(article_id, users_id):
            return False

        db = await active_secondary_db()

        record = UserRelationships(
            article_id=article_id,
            users_id=users_id,
        )

        db.add(record)
        db.commit()

        cls.with_cache(record)
        return record

    @classmethod
    async def delete(cls, article_id: int, users_id: int) -> bool:
        db = await active_secondary_db()

        stmt = select(UserRelationships).where(
            UserRelationships.article_id == article_id,
            UserRelationships.users_id == users_id,
        )

        record = db.execute(stmt).scalar_one_or_none()

        if record:
            db.delete(record)
            db.commit()

        LikesCached.discard((users_id, article_id))
        return True

    @classmethod
    async def exists(cls, article_id: int, users_id: int) -> bool:
        key = (users_id, article_id)

        if key in LikesCached:
            return True

        db = await active_secondary_db()

        stmt = select(UserRelationships).where(
            UserRelationships.users_id == users_id,
            UserRelationships.article_id == article_id,
        )

        record = db.execute(stmt).scalar_one_or_none()

        if not record:
            return False

        LikesCached.add(key)
        return True

    @classmethod
    async def handle_like(
        cls, *, article_id: int = None, users_id: int = None, option: str
    ):
        response = {
            "log_": random_string(45),
            "pam_": _Security.text_compressed(option),
        }

        if option == "removelike":
            response[option] = await cls.delete(article_id, users_id)
            return json_response([response, 200])

        if option == "like":
            await cls.insert(article_id, users_id)
            response[option] = True
            response["key_"] = random_string(58)
            return json_response([response, 200])

        response["error"] = "Invalid like option"
        return json_response([response, 400])

    @classmethod
    async def get_metrics(cls, article_id: int, users_id: int):
        feedback = (
            "article-like" if await cls.exists(article_id, users_id) else "feedback"
        )

        db = await active_secondary_db()

        stmt = (
            select(func.count())
            .select_from(UserRelationships)
            .where(UserRelationships.article_id == article_id)
        )

        likes = db.execute(stmt).scalar_one()

        return likes, feedback
