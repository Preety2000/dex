from includes.core.globals.entry import app_context

websocket_catch = {}


class AuthWebsocket:

    def __init__(self, websocket):
        conn_id = id(websocket)

        websocket_catch[conn_id] = websocket

    @staticmethod
    async def adding(websocket):
        member_id = await app_context.setting.member("id")
        conn_id = id(websocket)
        f"{conn_id}/{await app_context.setting.member("id")}"
