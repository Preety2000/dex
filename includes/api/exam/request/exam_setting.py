from includes.src.request import Request

from includes.core.globals.entry import app_context
from includes.core.security import AUTH_TOKEN


class CreateStore:
    KEY = "_cf_eSt"

    @staticmethod
    def _read(request: Request = None):
        return AUTH_TOKEN.decode(request.state.cookie.get(CreateStore.KEY)) or {}

    @staticmethod
    def set(key, value, request: Request = None):
        data = CreateStore._read()
        data[key] = value

        request.state.cookie.insert(CreateStore.KEY, AUTH_TOKEN.encode(data))

        return data

    @staticmethod
    def get(key=None):
        data = CreateStore._read()
        return data.get(key) if key else data

    @staticmethod
    def res(key=None, request: Request = None):
        if key:
            data = CreateStore._read()
            data.pop(key, None)

            request.state.cookie.insert(CreateStore.KEY, AUTH_TOKEN.encode(data))
            return data

        request.state.cookie.delete(CreateStore.KEY)
        return {}
