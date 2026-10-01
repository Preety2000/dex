from datetime import datetime, timedelta
from includes.core.security import _Security
from includes.core.repo.schemas.msg import UltraFastStore

EXPIRE_TIME_MINUTES = 10

session_temp = {}


class MsgExamRequestHandler:
    def __init__(self, id, exam_id):
        self.id = f"TH_{str(id).zfill(8)}"
        self.session = UltraFastStore(self.id)
        self.entry = _Security.short_encode(exam_id)

    async def _ensure_storage(self):
        session_temp[self.id] = session_temp.get(self.id, None)
        if session_temp[self.id] is None:
            session_temp[self.id] = await self.session.get()
            print(f"\033[1;96m{"_ensure_storage"}\033[0m")

    async def get(self, value=None):
        if value is None:
            value = {}

        await self._ensure_storage()
        data = session_temp[self.id].get(self.entry, {})
        return data.get("data", value)

    async def insert(self, value):
        if not self.entry:
            return False

        await self._ensure_storage()
        await self._delete_expired_internal()

        expire_time = datetime.now() + timedelta(minutes=7200)
        expire_ts = int(expire_time.timestamp())

        session_temp[self.id][self.entry] = {"data": value, "max_age": expire_ts}

        await self.session.save(session_temp[self.id])
        return True

    async def update(self, value):
        return await self.insert(value)

    async def set_entry(self, bind):
        await self._ensure_storage()
        self.entry = bind(list(session_temp[self.id].keys()) or [])
        return self.entry

    async def _delete_expired_internal(self):
        now = int(datetime.now().timestamp())
        session_temp[self.id] = {
            k: v for k, v in session_temp[self.id].items() if v.get("max_age", 0) > now
        }

    async def deleteExpiredData(self):
        await self._ensure_storage()

        await self._delete_expired_internal()
        await self.session.save(session_temp[self.id])  # ✅ controlled save
        return session_temp.get(self.entry, {})

    async def delete(self):
        await self._ensure_storage()

        if self.entry in session_temp[self.id]:
            del session_temp[self.id][self.entry]

        await self.session.save(session_temp[self.id])
        return session_temp.get(self.entry, {})


def _get_folder(folder):
    return folder.db_folder


class MsgExamController:
    def __init__(self, entry):
        self.storage = None
        self.session = UltraFastStore("stp_tamp", _get_folder)
        self.entry = entry

    async def _ensure_storage(self):
        if self.storage is None:
            self.storage = await self.session.get()

    async def get(self, value=None):
        await self._ensure_storage()

        data = self.storage.get(self.entry, {})
        print(f"\033[1;96m{data}\033[0m", data)
        return data.get("data", value)

    async def insert(self, value):
        if not self.entry:
            return False

        await self._ensure_storage()
        await self._delete_expired_internal()

        expire_time = datetime.now() + timedelta(minutes=EXPIRE_TIME_MINUTES)
        expire_ts = int(expire_time.timestamp())

        self.storage[self.entry] = {"data": value, "max_age": expire_ts}

        await self.session.save(self.storage)  # ✅ only one write
        return True

    async def update(self, value):
        return await self.insert(value)

    async def set_entry(self, bind):
        await self._ensure_storage()
        self.entry = bind(list(self.storage.keys()) or [])
        return self.entry

    async def _delete_expired_internal(self):
        now = int(datetime.now().timestamp())
        self.storage = {
            k: v for k, v in self.storage.items() if v.get("max_age", 0) > now
        }

    async def deleteExpiredData(self):
        await self._ensure_storage()

        await self._delete_expired_internal()
        await self.session.save(self.storage)
        return self.storage

    async def delete(self):
        await self._ensure_storage()

        if self.entry in self.storage:
            del self.storage[self.entry]

        await self.session.save(self.storage)
        return self.storage
