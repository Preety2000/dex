from sqlalchemy import or_, select

from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.db.connection import active_primary_db
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
                f"/media/u/{get_email_folder_info(record['id'])}/"
                f"{record.get('image_src', _Security.short_encode('image.png'))}"
                if k == "img"
                else record.get(k)
            )
            for k in keys
        }

    @staticmethod
    async def get_with_secret(secret: str) -> dict:
        cached_id = MemberCacheData.BySecret.get(secret)

        if cached_id:
            return await MemberCache.get_with_id(cached_id)

        stmt = select(Members).where(Members.secret == secret).limit(1)
        db = await active_primary_db()
        result = db.execute(stmt)
        record = result.scalar_one_or_none()

        return MemberCache._cache(record) if record else None

    @staticmethod
    async def get_with_id(
        id: int,
        keys: list[str] = None,
    ) -> dict:

        id = int(id)

        record = MemberCacheData.ById.get(id)

        if record:
            return MemberCache.filters(record, keys)

        stmt = select(Members).where(Members.id == id).limit(1)
        db = await active_primary_db()
        result = db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        return MemberCache.filters(
            MemberCache._cache(record),
            keys,
        )

    @staticmethod
    async def getrollnumber(rollnumber: int):
        userid = extract_id_from_roll(rollnumber)

        record = await MemberCache.get_with_id(userid)

        return serialize_member(record) if record else None

    @staticmethod
    async def get(query: int | str) -> dict:

        stmt = (
            select(Members)
            .where(
                or_(
                    Members.id == query,
                    Members.email == query,
                    Members.phone == query,
                    Members.secret == query,
                )
            )
            .limit(1)
        )
        db = await active_primary_db()
        result = db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        return MemberCache._cache(record)

    @staticmethod
    async def get_many(
        id_list: list[int],
        keys: list[str] = None,
    ):
        records = []
        missing = []

        for qid in id_list or []:
            qid = int(qid)

            record = MemberCacheData.ById.get(qid)

            if record:
                records.append(MemberCache.filters(record, keys))
            else:
                missing.append(qid)

        if missing:
            stmt = select(Members).where(Members.id.in_(missing))

            db = await active_primary_db()
            result = db.execute(stmt)
            db_records = result.scalars().all()

            records.extend(
                MemberCache.filters(
                    MemberCache._cache(record),
                    keys,
                )
                for record in db_records
            )

        return records
