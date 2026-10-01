# await websocket.accept()	WebSocket connection accept karta hai (mandatory)
# await websocket.receive_text()	Text message receive karta hai
# await websocket.receive_bytes()	Binary message receive karta hai
# await websocket.send_text()	Text message bhejta hai
# await websocket.send_bytes()	Binary data bhejta hai
# await websocket.close()	WebSocket close karta hai
# websocket.client	(host, port) tuple of client IP
# websocket.url	Full URL of WebSocket request
# websocket.headers	Request headers (case-insensitive dict)
# websocket.cookies	Cookies from the request
# websocket.query_params	Query parameters from URL
# websocket.path_params	Path parameters from route
# websocket.scope	ASGI scope dictionary (advanced use)
# websocket.application_state	Internal ASGI state
# websocket.client_state	WebSocketState enum – current connection state
# websocket.receive_json()	JSON message receive karta hai (FastAPI-specific)
# websocket.send_json()	JSON message send karta hai (FastAPI-specific)
# websocket.close_code	(After disconnect) – Close code received


import asyncio
import json
import logging
import time
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from redis import asyncio as aioredis
from fastapi import WebSocket, WebSocketDisconnect
from includes.api.chat.socket.index import ChatSokete
from includes.api.router import DynamicSokitURLRoute
from includes.core.globals.entry import app_context
from includes.api.exam.session.ev import STUDENT_LIVE_IN_EXAME
from includes.api.exam.socket.index import ExameSokete
from includes.middleware.auth_websocket import AuthWebsocket
from includes.src.chat.relationships import ChatRelationships

# Global dictionary to store state for each connection
connection_states = {}
connections = []


def json_to_binary(json_obj):
    json_str = json.dumps(json_obj)
    return json_str.encode("utf-8")


def object_to_binary(obj):
    json_str = json.dumps(obj)
    return json_str.encode("utf-8")


def binary_to_json(binary_data):
    json_str = binary_data.decode("utf-8")
    return json.loads(json_str)


logger = logging.getLogger("apiws")
logging.basicConfig(level=logging.INFO)


async def senddata(websocket, query: dict):
    try:
        conn_id = id(websocket)
    except Exception:
        conn_id = None

    try:
        await websocket.send_bytes(object_to_binary(query))
        return True

    except WebSocketDisconnect as e:
        if conn_id and conn_id in connection_states:
            del connection_states[conn_id]

        setattr(websocket, "states", False)
        print("websocket close error 1", e)
        return False

    except Exception as e:
        if conn_id and conn_id in connection_states:
            del connection_states[conn_id]

        setattr(websocket, "states", False)
        print("websocket close error 2", e)
        return False


async def incoming_timeout(ws, timeout=1):
    try:
        return await asyncio.wait_for(ws.receive(), timeout)
    except asyncio.TimeoutError:
        return None
    except asyncio.CancelledError:
        logger.warning("WebSocket receive task was cancelled.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during websocket receive: {e}")
        return None


class APIWS:
    def __init__(self, websocket: WebSocket):
        self.sub_channel = None
        self.pub_channel = None
        self.subscriber_task = None
        self.websocket = websocket

        self.redis = aioredis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

    async def redis_subscriber(self):
        if not self.sub_channel:
            return

        # Create pubsub instance
        pubsub = self.redis.pubsub()
        try:
            await pubsub.subscribe(self.sub_channel)
            async for message in pubsub.listen():
                if message is None:
                    continue

                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await senddata(self.websocket, data)
                    except Exception as e:
                        logger.error(f"Redis message error: {e}")

        except asyncio.CancelledError:
            logger.info("Redis subscriber cancelled")

        except Exception as e:
            logger.error(f"Redis subscriber error: {e}")

        finally:
            try:
                await pubsub.unsubscribe(self.sub_channel)
            except:
                pass
            await pubsub.close()
            logger.info("Redis pubsub closed")

    async def entry(self, incoming, roots: DynamicSokitURLRoute):
        # conn_id = id(self.websocket)

        if roots.scope_type == "exam":
            clsexco = ExameSokete(self.websocket)
            data = await clsexco.websocket_handler(incoming, roots)
            return data, None

        elif roots.scope_type == "chat":
            clsexco = ChatSokete(self.websocket)
            clsexco.roots = roots
            data = await clsexco.chat_index(incoming)
            return data, None

        return None, None

    async def index(self, root):
        # scope_type/scope_slug/resource_type/resource_slug/sub_action/child_entity/modifier
        # authWebsocket = AuthWebsocket(self.websocket)

        is_time = time.time()
        self.websocket.state.member = await app_context.setting.member()
        if not self.websocket.state.member:
            await self.websocket.close(code=1008)
            print("Connection rejected: Unauthorized access")
            return

        self.websocket.state.disconnect_callback = {}
        await self.websocket.accept()

        try:
            while True:
                # Await incoming data with a timeout of 0.01 seconds
                incoming = await incoming_timeout(self.websocket, 0.01)

                if incoming:
                    try:
                        incoming = incoming["bytes"].decode("utf-8")
                        if isinstance(incoming, str):
                            try:
                                incoming = json.loads(incoming)
                            except:
                                pass

                    except Exception as e:
                        # Optionally send a message back to client indicating invalid data
                        await self.websocket.send_json(
                            {"error": "Invalid data received"}
                        )
                        break  # Optionally break or close connection after error

                # Initialize the outgoing data based on the received input
                outgoing, callBack = await self.entry(
                    incoming, DynamicSokitURLRoute.parse(root)
                )
                if outgoing:
                    is_time = time.time()  # Reset counter after sending logger action
                    action = await senddata(self.websocket, outgoing)

                    # Call the callback function if it's defined
                    if callable(callBack):
                        await callBack(action)

                    if action is False:
                        break  # Stop the loop if action returns False

                # if (time.time() - is_time) > 5:
                if (time.time() - is_time) > 2:
                    is_time = time.time()  # Reset counter after sending logger action

                    # Stop if action returns False
                    if self.websocket.application_state != WebSocketState.CONNECTED:
                        print(
                            "self.websocket.application_state != WebSocketState.CONNECTED"
                        )
                        break

                    # action = await senddata(self.websocket, {"logger": True})
                    # if action is False:
                    #     break  # Stop if action returns False

        except Exception as e:
            disconnect_callback = getattr(
                self.websocket.state, "disconnect_callback", {}
            )
            for callback in disconnect_callback.values():
                if callable(callback):
                    await callback()

                print("websocket close error 3", callback)

            try:
                roll_no = self.websocket.state.member.get("roll_no")
                if "ws/exam/attach/q" in str(self.websocket.url):
                    STUDENT_LIVE_IN_EXAME[roll_no] = None

            except:
                pass

            print(f"WebSocket error: {e}")
            # Log any unexpected errors that occur during the WebSocket loop

        finally:
            try:
                # Close the WebSocket gracefully if it's still open
                if self.websocket.application_state != WebSocketState.DISCONNECTED:
                    await self.websocket.close()

            except RuntimeError:
                pass  # Handle possible runtime errors during WebSocket close
