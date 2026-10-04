from includes.core.config import main_database
from includes.core.security import _Security
from includes.database.models.owner import Members
from includes.database.connection import active_primary_db
from includes.utils.meb import get_email_folder_info


class CHCUSER:

    # Serialize member object to JSON
    def jsons(self, member, callback=None):
        short_encode = _Security.short_encode
        img = (
            short_encode(member.image_src)
            if member.image_src and "/" in member.image_src
            else (member.image_src or "image.png")
        )
        user_data = {
            "id": member.id,
            "name": member.name,
            "userName": member.username,
            "bio": member.biography,
            "img": f"/media/u/{get_email_folder_info(member.id)}/{img}",
            "__m": f"MJ{member.id}E",
            "verify": True,
            "account_type": 1,
        }
        return callback(user_data, member) if callback else user_data

    def getIdList(self, ids, callback):
        with main_database() as db:
            allUser = db.query(Members).filter(Members.id.in_(ids)).all()
            return [self.jsons(item, callback) for item in allUser]

    async def getchatdata(self, Q1=None, Q2=None):
        db = await active_primary_db()

        allUser = db.query(Members).all()
        return [self.jsons(item) for item in allUser]
