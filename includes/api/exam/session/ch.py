import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from includes.db.models.utils import TimeStamp
from includes.core.globals.entry import app_context
from includes.core.globals.coreutils import generate_unique_uuid
from includes.db.dataclass import serialize


@dataclass
class ExamContext:
    exam_name: list | None = None
    exam_meta: list | None = None
    exam_qsto: list | None = None
    timestamp: int = field(default_factory=TimeStamp.now_timestamp)


class ExamCacheMemory:

    _last_cleanup: int = TimeStamp.now_timestamp()
    _expire_after = 24 * 60 * 60 * 1000  # 24 hours in ms
    _cleanup_interval = 40 * 60 * 1000  # 40 minutes in ms

    @staticmethod
    def ensure_file_path(entry: str = None, create_if_missing: bool = False):

        if not entry:
            return None

        file_path = Path(app_context.folder.ex_context) / entry
        if create_if_missing and not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with file_path.open("w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

        if file_path.exists():
            return str(file_path)

        return None

    @classmethod
    async def get(
        cls, entry: str, default: ExamContext | None = None
    ) -> ExamContext | None:
        file_path = ExamCacheMemory.ensure_file_path(entry)
        if file_path is None:
            return default

        with open(file_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
            return ExamContext(**data)

    @classmethod
    async def add(cls, entry: str, data: ExamContext) -> str:
        now = TimeStamp.now_timestamp()

        if not entry:
            files = os.listdir(app_context.folder.ex_context)
            entry = generate_unique_uuid(files)

        data = serialize(data)
        file_path = ExamCacheMemory.ensure_file_path(entry, True)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        if now - cls._last_cleanup >= cls._cleanup_interval:
            cls.cleanup(now)

        return entry

    @classmethod
    def remove(cls, entry: str) -> bool:
        """Remove cache file by entry name."""

        file_path = cls.ensure_file_path(entry)

        if file_path is None:
            return False

        try:
            Path(file_path).unlink()
            return True
        except OSError:
            return False

    @classmethod
    def cleanup(cls, now: int | None = None) -> int:
        """Remove cache files older than expire time."""

        if now is None:
            now = TimeStamp.now_timestamp()

        folder = Path(app_context.folder.ex_context)

        if not folder.exists():
            return 0

        expire_before = now - cls._expire_after
        removed = 0

        for file in folder.iterdir():

            if not file.is_file():
                continue

            # file modified time in ms
            modified_time = int(file.stat().st_mtime)

            if modified_time < expire_before:
                try:
                    file.unlink()
                    removed += 1
                except OSError:
                    pass

        cls._last_cleanup = now

        return removed

    @classmethod
    def size(cls) -> int:
        """Return number of cached files."""

        folder = Path(app_context.folder.ex_context)

        if not folder.exists():
            return 0

        return sum(1 for file in folder.iterdir() if file.is_file())
