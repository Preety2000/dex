from typing import List
from fastapi import WebSocket


class ChatManager :
    def __init__(self):
        self.deft = {}


class RealtimeChat :
    def __init__(self):
        
        self.deft = {}



class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, message: str):
        if user_id in self.connections:
            await self.connections[user_id].send_text(message)

