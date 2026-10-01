import os
import msgpack
import asyncio
import aiofiles
from includes.core.repo.dir_manager import folder


def _get_folder(folder):
    return folder.educore


def _get_filepath(folder_path, filename):
    return os.path.join(folder_path, f"{filename}.msg")


class MsgPackHandler:
    def __init__(self, filename):
        self.filename = filename
        self.filepath = _get_filepath(folder.db_folder, filename)


    async def get(self):
        """Read and unpack the msgpack file, returning its content."""
        if not os.path.exists(self.filepath):
            await self.save({})
            return {}

        try:
            async with aiofiles.open(self.filepath, "rb") as file:
                content = await file.read()
                return msgpack.unpackb(content, raw=False)  # Fix applied here
        except (msgpack.exceptions.UnpackException, ValueError):
            # ValueError handles the `strict_map_key=True` case if missed
            os.remove(self.filepath)
            await self.save({})
            return {}

    async def save(self, data):
        """Serialize and save data to msgpack file."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        packed = msgpack.packb(data, use_bin_type=True)
        async with aiofiles.open(self.filepath, "wb") as file:
            await file.write(packed)

    async def delete(self):
        """Delete the msgpack file if it exists."""
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
            return True
        return False


class UltraFastStore:
    def __init__(self, filename, bind=_get_folder):
        self._cache = {}
        self._loaded = False
        self._dirty = False
        self._flush_task = None
        self._lock = asyncio.Lock()
        self.filepath = _get_filepath(bind(folder), filename)

    # -------------------------
    # LOAD
    # -------------------------
    async def load(self):
        if self._loaded:
            return

        if not os.path.exists(self.filepath):
            self._loaded = True
            return

        try:
            async with aiofiles.open(self.filepath, "rb") as f:
                content = await f.read()
                self._cache = msgpack.unpackb(content, raw=False, strict_map_key=False)

        except Exception as e:
            print(f"\033[1;91m LOAD ERROR{e}\033[0m")
            print("LOAD ERROR:", self.filepath)
            self._cache = {}

        self._loaded = True

    # -------------------------
    # GET
    # -------------------------
    async def get(self):
        await self.load()
        return self._cache

    # -------------------------
    # SAVE (ULTRA FAST)
    # -------------------------
    async def save(self, data):
        await self.load()
        async with self._lock:
            # merge instead of overwrite
            self._cache.update(data)
            self._dirty = True

            # start flush loop if not running
            if self._flush_task is None or self._flush_task.done():
                self._flush_task = asyncio.create_task(self._flush_loop())

    # -------------------------
    # FLUSH LOOP (BATCH WRITES)
    # -------------------------
    async def _flush_loop(self):
        while self._dirty:
            await asyncio.sleep(1)  # batch window

            async with self._lock:
                if not self._dirty:
                    return

                data = self._cache.copy()
                self._dirty = False

            await self._write(data)

    # -------------------------
    # DISK WRITE (ATOMIC)
    # -------------------------
    async def _write(self, data):
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            packed = msgpack.packb(data, use_bin_type=True)
            async with aiofiles.open(self.filepath, "wb") as f:
                await f.write(packed)

                print(f"\033[1;92m{'File Save'}\033[0m")
                print(f"\033[1;92m{data}\033[0m")

        except Exception as e:
            print("WRITE ERROR:", e)
            print(f"\033[1;92m{self.filepath}\033[0m")
