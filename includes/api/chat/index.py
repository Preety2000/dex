from dataclasses import dataclass
from typing import Any

from includes.core.globals.entry import app_context
from includes.src.chat.relationships import ChatRelationships
from includes.utils.utils import get_post_value


@dataclass
class RequestObject:
    request_code: int = None
    action: str = None
    payload: Any = None
    more_data: Any = None


def g(lst, i):
    return lst[i] if isinstance(lst, list) and i < len(lst) else None


def parse_request(data):
    action = g(data, 1)
    return RequestObject(
        request_code=g(data, 0),
        action=g(action, 0),
        payload=g(action, 1),
        more_data=g(action, 2),
    )


class CHAIT:

    @staticmethod
    async def index():

        async def friendships_action(rq_action: RequestObject):
            friendships = ChatRelationships(await app_context.setting.member("id"))
            if rq_action.action == "chats":
                data = await friendships.getChatList()
                return {"__ac": {5001: data}}

            if rq_action.action == "request":
                data = await friendships.getRequestList()
                return {"__ac": {5002: data}}

            if rq_action.action == "search":
                data = await friendships.getSearchList()
                return {"__ac": {5003: data}}

            return {}

        request_handlers = {
            400: friendships_action,
        }

        for request in await get_post_value(True, []):
            request_data = parse_request(request)
            handler = request_handlers.get(request_data.request_code)

            if callable(handler):
                return await handler(request_data)
