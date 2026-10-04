from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.database.dataclass.dataclass import serialize
from includes.database.models.owner import Beckup


class ClassBeckup:

    @staticmethod
    async def insert(content, types):

        if app_context.response["error"]:
            return None

        try:
            title = content.get(
                "title", content.get("name", _Security.short_encode(content.get("id")))
            )
            app_context.db.add(
                Beckup(
                    types=types,
                    title=title,
                    content=serialize(content),
                )
            )
            app_context.db.commit()
            return True

        except:
            return None
