from dataclasses import dataclass
import json

from includes.api.chat.utils import ChatAction
from includes.src.chat.relationships import ChatRelationships, relationships_store


class ChatSokete:
    def __init__(self, request):
        self.request = request
        self.websocket = request

        self.countdown = False
        self.tamp_store = self.websocket.state.tamp = {}

    async def handle_chat_event(self, incoming, relationships):
        if not isinstance(incoming, list) or len(incoming) != 4:
            return

        chait_action = ChatAction(incoming)
        method = getattr(relationships, chait_action.action_name, None)
        if callable(method):
            return await method(chait_action)

        print("chait_action", chait_action)

        return None

    async def chat_index(self, incoming):

        # print("active")

        self.relationships = ChatRelationships(
            int(self.websocket.state.member.get("id"))
        )

        if responce := await self.handle_chat_event(incoming, self.relationships):
            return responce

        session = relationships_store.setdefault(self.relationships.id, {})
        event = session.setdefault("event", [])
        # Redis Pub/Sub channel
        # self.pub_channel = "chat"
        # self.sub_channel = "chat"

        action_map = {
            "statusUpdate": 400,
            "addMessage": 401,
            "removeMessage": 402,
            "statusCheck": 403,
            "messageStatusUpdate": 404,
        }

        if event:
            print("event", event)
            item = event.pop(0)
            value = item.get("value")
            action_code = action_map.get(item.get("action"))

            async def statusMessageUpdate(action):
                if action == True:
                    recv_id = item.get("recv_id")
                    if action_code == 401 and recv_id:
                        await self.relationships.messageUpdated(
                            value["ChatBox"], recv_id, value["massid"], 1
                        )
                        return None

                if action == False:
                    event.append(item)
                    return False

            if action_code and value:
                return {"__ac": {action_code: value}}
        else:
            await self.relationships.onchange_event(event)

        return None
