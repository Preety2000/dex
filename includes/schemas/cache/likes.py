from typing import Optional

from includes.core.globals.fun import random_string
from includes.utils.utils import json_response
from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.db.models.secondary import UserRelationships

LikesCatchd: set[tuple[int, int]] = set()


class Likes:

    @classmethod
    def with_catch(cls, record):

        primary_key = (record.users_id, record.article_id)
        LikesCatchd.add(primary_key)

        return record

    @classmethod
    def get(cls, article_id: int, users_id: int) -> Optional[UserRelationships]:

        primary_key = (users_id, article_id)
        record = (
            app_context.db.query(UserRelationships)
            .filter(
                UserRelationships.users_id == users_id,
                UserRelationships.article_id == article_id,
            )
            .first()
        )

        if record is None:
            return None

        if primary_key not in LikesCatchd:
            cls.with_catch(record)

        return record

    @classmethod
    def insert(cls, article_id: int, users_id: int) -> UserRelationships:

        if cls.get(article_id, users_id):
            return False

        record = UserRelationships(
            article_id=article_id,
            users_id=users_id,
        )

        app_context.db.add(record)
        app_context.db.commit()

        cls.with_catch(record)

        return record

    @classmethod
    def delete(cls, article_id: int, users_id: int) -> bool:

        app_context.db.query(UserRelationships).filter(
            UserRelationships.article_id == article_id,
            UserRelationships.users_id == users_id,
        ).delete()

        app_context.db.commit()

        LikesCatchd.discard((users_id, article_id))

        return True

    @classmethod
    def exists(cls, article_id: int, users_id: int) -> bool:

        primary_key = (users_id, article_id)
        if primary_key in LikesCatchd:
            return True

        record = (
            app_context.db.query(UserRelationships)
            .filter(
                UserRelationships.users_id == users_id,
                UserRelationships.article_id == article_id,
            )
            .first()
        )

        if record is None:
            return False

        LikesCatchd.add(primary_key)

        return True

    @classmethod
    def handle_like(cls, *, article_id: int = None, users_id: int = None, option: str):
        response = {
            "log_": random_string(45),
            "pam_": _Security.text_compressed(option),
        }

        if option == "removelike":
            response[option] = cls.delete(article_id, users_id)
            return json_response([response, 200])

        if option == "like":
            cls.insert(article_id, users_id)
            response[option] = True
            response["key_"] = random_string(58)

            return json_response([response, 200])

        # Unknown option
        response["error"] = "Invalid like option"

        return json_response([response, 400])
