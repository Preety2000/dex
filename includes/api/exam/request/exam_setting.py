from includes.core.globals.entry import app_context
from includes.core.security import AUTH_TOKEN


class CreateStore:
    KEY = "_cf_eSt"

    @staticmethod
    def _read():
        return AUTH_TOKEN.decode(app_context.cookie.get(CreateStore.KEY)) or {}

    @staticmethod
    def set(key, value):
        data = CreateStore._read()
        data[key] = value

        app_context.cookie.insert(CreateStore.KEY, AUTH_TOKEN.encode(data))

        return data

    @staticmethod
    def get(key=None):
        data = CreateStore._read()
        return data.get(key) if key else data

    @staticmethod
    def res(key=None):
        if key:
            data = CreateStore._read()
            data.pop(key, None)

            app_context.cookie.insert(CreateStore.KEY, AUTH_TOKEN.encode(data))
            return data

        app_context.cookie.delete(CreateStore.KEY)
        return {}
