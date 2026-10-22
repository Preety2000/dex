from includes.src.request import Request

from includes.core.globals.entry import app_context
from includes.core.security import AUTH_TOKEN


class _FileAuthor:
    KEY = "_md_trg"

    def __init__(self, request: Request):
        self.request = request

    def _read(self):
        return AUTH_TOKEN.decode(self.request.state.cookie.get(self.KEY)) or {}

    def set(self, key, value):
        data = self._read()
        data[key] = value

        self.request.state.cookie.insert(self.KEY, AUTH_TOKEN.encode(data))

        return data

    def get(self, key=None):
        data = self._read()
        return data.get(key) if key else data

    def res(self, key=None):
        if key:
            data = self._read()
            data.pop(key, None)

            self.request.state.cookie.insert(self.KEY, AUTH_TOKEN.encode(data))
            return data

        self.request.state.cookie.delete(self.KEY)
        return {}
