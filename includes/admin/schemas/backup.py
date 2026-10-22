from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.database.connection import config_primary_db
from includes.database.dataclass.dataclass import serialize
from includes.database.models.primary import Beckup


class ClassBeckup:

    @staticmethod
    async def insert(request, content, types):
        db = await config_primary_db()

        if request.state.response["error"]:
            return None

        try:
            title = content.get(
                "title", content.get("name", _Security.short_encode(content.get("id")))
            )
            db.add(
                Beckup(
                    types=types,
                    title=title,
                    content=serialize(content),
                )
            )
            db.commit()
            return True

        except:
            return None
