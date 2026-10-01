from dataclasses import dataclass


@dataclass(init=False)
class ChatAction:
    action_name: str
    chatbox: str
    recv_id: int
    payload: str | list | dict
    declaration: list | dict

    def __init__(self, incoming):
        self.action_name = incoming[0]
        self.chatbox = incoming[1][0]
        self.recv_id = incoming[1][1]
        self.payload = incoming[2]
        self.declaration = incoming[3]
