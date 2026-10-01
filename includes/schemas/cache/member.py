from sqlalchemy import or_
from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.db.dataclass import serialize
from includes.db.models.owner import Members
from includes.utils.meb import (
    extract_id_from_roll,
    get_email_folder_info,
    serialize_member,
)
from includes.schemas.cache.dataclass import _MemberCache

MemberCacheData = _MemberCache()


class MemberCache:

    @staticmethod
    def _cache(record: Members) -> dict:
        print("[call MemberCache]")
        _record = serialize(record)

        MemberCacheData.ById[record.id] = _record
        MemberCacheData.ByEmail[record.email] = record.id
        MemberCacheData.BySecret[record.secret] = record.id

        return _record

    @staticmethod
    async def delete_cache(id: int):
        print("[call MemberCache Delete]")

        try:
            id = int(id)

            if id in MemberCacheData.ById:
                del MemberCacheData.ById[id]

            return True

        except Exception as e:
            print(f"Delete cache error: {e}")
            return False

    @staticmethod
    def filters(record, keys):
        if not keys:
            return record

        return {
            k: (
                f"/media/u/{get_email_folder_info(record["id"])}/{record.get('image_src', _Security.short_encode('image.png'))}"
                if k == "img"
                else record.get(k)
            )
            for k in keys
        }

    @staticmethod
    async def get_with_secret(secret: str) -> dict:

        if MemberCacheData.BySecret.get(secret):
            return await MemberCache.get_with_id(MemberCacheData.BySecret[secret])

        record = app_context.db.query(Members).filter(Members.secret == secret).first()
        return MemberCache._cache(record) if record else None


    @staticmethod
    async def get_with_id(id: int, keys: list[str] = None) -> dict:

        record = MemberCacheData.ById.get(int(id))
        if record:
            return MemberCache.filters(record, keys)

        record = app_context.db.query(Members).filter(Members.id == int(id)).first()
        return MemberCache.filters(MemberCache._cache(record), keys) if record else None

    @staticmethod
    async def getrollnumber(rollnumber: int):
        userid = extract_id_from_roll(rollnumber)
        record = await MemberCache.get_with_id(userid)
        return serialize_member(record)

    @staticmethod
    async def get(query: int | str) -> dict:

        record = (
            app_context.db.query(Members)
            .filter(
                or_(
                    Members.id == query,
                    Members.email == query,
                    Members.phone == query,
                    Members.secret == query,
                )
            )
            .first()
        )

        if not record:
            return None

        return MemberCache._cache(record)

    @staticmethod
    async def get_many(id_list: list[int], keys: list[str] = None):
        records = []
        missing = []

        for qid in id_list or []:
            record = MemberCacheData.ById.get(qid)
            (
                records.append(MemberCache.filters(record, keys))
                if record
                else missing.append(qid)
            )

        if missing:
            records.extend(
                MemberCache.filters(MemberCache._cache(record), keys)
                for record in app_context.db.query(Members)
                .filter(Members.id.in_(missing))
                .all()
            )

        return records
