from includes.core.globals.entry import app_context
from includes.core.security import AUTH_TOKEN


class _FileAuthor:
    KEY = "_md_trg"

    @classmethod
    def _read(cls):
        return AUTH_TOKEN.decode(app_context.cookie.get(cls.KEY)) or {}

    @classmethod
    def set(cls, key, value):
        data = cls._read()
        data[key] = value

        app_context.cookie.insert(cls.KEY, AUTH_TOKEN.encode(data))

        return data

    @classmethod
    def get(cls, key=None):
        data = cls._read()
        return data.get(key) if key else data

    @classmethod
    def res(cls, key=None):
        if key:
            data = cls._read()
            data.pop(key, None)

            app_context.cookie.insert(cls.KEY, AUTH_TOKEN.encode(data))
            return data

        app_context.cookie.delete(cls.KEY)
        return {}
