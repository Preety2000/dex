import copy
import json
import logging
from sqlalchemy import and_, asc, desc, or_
from includes.database.models.utils import TimeStamp
from includes.api.chat.utils import ChatAction
from includes.core.globals.coreutils import generate_unique_uuid
from includes.database.chait.chatModel import (
    chatBase,
    ChatBoxDatabace,
    FriendShip,
    UserSetting,
)
from includes.database.chait.sql import LocalDB
from includes.services.member.chcuser import CHCUSER

# __m = frind donm data-id

logger = logging.getLogger("websocket")
logging.basicConfig(level=logging.INFO)


def get_adder_timestamp(offset=None):
    return int(TimeStamp.now_timestamp()) - (offset or 0)


async def get_member_database(member_id: int):
    database = LocalDB(f"DB{member_id}X", chatBase, "db_console")

    tables = await database.register_tables([FriendShip, UserSetting, ChatBoxDatabace])
    return database, tables


async def get_message_box(user1, user2, friendship_id):
    database, db_tables = await get_member_database(user1)
    friendship = database.friendship.filter(
        or_(
            and_(
                db_tables.friendship.first_user == user1,
                db_tables.friendship.second_user == user2,
            ),
            and_(
                db_tables.friendship.first_user == user2,
                db_tables.friendship.second_user == user1,
            ),
        )
    ).first()

    if not friendship:
        friendship = db_tables.friendship(
            first_user=user1, second_user=user2, friendship_id=friendship_id
        )
        database.session.add(friendship)
        database.session.commit()

    return database, db_tables, friendship


def getMessageId(a, b):
    return a + b + get_adder_timestamp(10000000)


relationships_store = {}


class ChatRelationships:
    def __init__(self, id):
        self.id = id
        self.member = CHCUSER()

    def get_session(self, id, option=None, default=None):
        if default == None:
            default = {}
        session = relationships_store.setdefault(id, {})
        return (session, session.setdefault(option, default)) if option else session

    def add_event(self, event_id, _event):
        s, event = self.get_session(event_id, "event", [])
        event.append(_event)

    async def initialize(self, recv_id):
        oursids = copy.copy(self.id)
        session_key = f"SEE{oursids}{recv_id}"
        cached_data = getattr(self, session_key, None)

        if not cached_data:
            friendship_id = f"MZ{oursids}{recv_id}"
            database1, db_tables1, frenship1 = await get_message_box(
                oursids, recv_id, friendship_id
            )
            database2, db_tables2, frenship2 = await get_message_box(
                recv_id, oursids, friendship_id
            )
            cached_data = {
                "our_class": db_tables1,
                "our_database": database1,
                "our_frenship": frenship1,
                "recv_class": db_tables2,
                "recv_database": database2,
                "recv_frenship": frenship2,
            }

            setattr(self, session_key, cached_data)

        return cached_data

    async def ons(self, chatAction: ChatAction):
        oursids = copy.copy(self.id)
        s, query = self.get_session(chatAction.chatbox, "chatbox", {})
        query = query.setdefault(oursids, {})

        status = chatAction.payload
        if query.get("status") != status:
            query["status"] = status
            query["lasttime"] = get_adder_timestamp()

    async def messageUpdated(self, chatAction: ChatAction, status: int = 2):
        oursids = copy.copy(self.id)
        if not chatAction.recv_id:
            return

        messageid = chatAction.payload
        initialize = await self.initialize(chatAction.recv_id)

        if chatAction.recv_id == oursids:
            logger.error(
                f"recv_id == oursids => Seme id {chatAction.recv_id} || {oursids}"
            )

        # our session
        our_clss = initialize.get("our_class")
        our_database = initialize.get("our_database")
        our_query = our_database.chatship.filter(
            our_clss.chatship.id == messageid
        ).first()

        # friend sesssion
        recv_clss = initialize.get("recv_class")
        recv_database = initialize.get("recv_database")
        recv_query = recv_database.chatship.filter(
            recv_clss.chatship.id == messageid
        ).first()

        # Retrieve session and event list for the receiver
        if our_query and recv_query:
            our_query.status = status
            our_database.session.commit()

            recv_query.status = status
            recv_database.session.commit()

            # Append the addMessage event to the event list
            self.add_event(
                chatAction.recv_id,
                {
                    "action": "messageStatusUpdate",
                    "value": {
                        "massid": messageid,
                        "chatBox": chatAction.chatbox,
                        "status": status,
                        "__n": f"MJ{oursids}E",
                    },
                },
            )

    async def sendmessage(self, chatAction: ChatAction):
        oursids = copy.copy(self.id)
        if not chatAction.recv_id:
            return
        initialize = await self.initialize(chatAction.recv_id)

        message = chatAction.payload.get("__ms")
        massid = chatAction.payload.get("massid")
        timestamp = chatAction.payload.get("timestamp")

        s, our_last_msg_from = self.get_session(oursids, "latest_msgs ", {})
        s, recv_last_msg_from = self.get_session(chatAction.recv_id, "latest_msgs ", {})

        messageid = getMessageId(oursids, chatAction.recv_id)

        our_frenship = initialize.get("our_frenship")
        if friendship_id := our_frenship.friendship_id:

            our_clss = initialize.get("our_class")
            our_database = initialize.get("our_database")
            our_nquery = our_clss.chatship(
                id=messageid,
                message=message,
                friendship=friendship_id,
                timestamp=timestamp,
                sender_id=oursids,
                status=0,
                zone=0,
            )
            our_database.session.add(our_nquery)
            our_database.session.commit()

            recv_clss = initialize.get("recv_class")
            recv_database = initialize.get("recv_database")
            nquery = recv_clss.chatship(
                id=messageid,
                message=message,
                friendship=friendship_id,
                timestamp=timestamp,
                sender_id=oursids,
                status=0,
                zone=0,
            )
            recv_database.session.add(nquery)
            recv_database.session.commit()

            # Construct the message query dictionary
            our_class = initialize.get("our_class")
            our_database = initialize.get("our_database")
            chatship = our_database.chatship.filter(
                and_(
                    ChatBoxDatabace.message == message,
                    ChatBoxDatabace.timestamp == timestamp,
                )
            ).first()
            query = {
                "__ms": message,
                "__d": chatship.gettuppel(chatAction.recv_id),
                "chatBox": chatAction.chatbox,
                "timestamp": timestamp,
                "__m": f"MJ{chatAction.recv_id}E",
                "__n": f"MJ{oursids}E",
                "omassid": massid,
                "massid": chatship.id,
            }

            recv_last_msg_from[chatAction.recv_id] = copy.copy(query)

            # Append the addMessage event to the event list
            self.add_event(
                chatAction.recv_id,
                {
                    "action": "addMessage",
                    "value": copy.deepcopy(query),
                    "recv_id": oursids,
                },
            )

            # Update query action
            query["__n"] = f"MJ{chatAction.recv_id}E"
            query["__d"] = chatship.gettuppel(oursids)

            our_last_msg_from[oursids] = copy.deepcopy(query)
            return {"__ac": {401: query}}

        return {"friendship": None}

    async def get(self, chatAction: ChatAction):
        if not chatAction.recv_id:
            return

        oursids = copy.copy(self.id)
        initialize = await self.initialize(chatAction.recv_id)

        our_class = initialize.get("our_class")
        our_frenship = initialize.get("our_frenship")
        our_database = initialize.get("our_database")
        our_frenship.friendship_id

        lasstMassageId, lasstMassageTimestamp, limit = (
            chatAction.payload
            if isinstance(chatAction.payload, list) and len(chatAction.payload) == 3
            else [None, None, 10]
        )

        if our_frenship.friendship_id == chatAction.chatbox:
            query = our_database.chatship.filter_by(friendship=chatAction.chatbox)
            logger.error(f"Exception => {lasstMassageId } {lasstMassageTimestamp}")

            if lasstMassageId and lasstMassageTimestamp:
                query = query.filter(
                    or_(
                        ChatBoxDatabace.timestamp < lasstMassageTimestamp,
                        and_(
                            ChatBoxDatabace.timestamp == lasstMassageTimestamp,
                            ChatBoxDatabace.id < lasstMassageId,
                        ),
                    )
                )

            query = query.order_by(desc(ChatBoxDatabace.timestamp)).limit(limit).all()

            def json(item):
                return {
                    "__ms": item.message,
                    "zone": item.zone,
                    "status": item.status,
                    "__d": item.gettuppel(oursids),
                    "massid": item.id,
                    "timestamp": item.timestamp,
                }

            data = [json(item) for item in query]
            if data:
                return {"__ac": {5004: data}, "chatBox": chatAction.chatbox}

            return {
                "__ac": {406: {"lasstMassage": False, "chatBox": chatAction.chatbox}}
            }

        return {
            "ourid": oursids,
            "sss": our_frenship.friendship_id == chatAction.chatbox,
            "friendship_id": our_frenship.friendship_id,
            "query": str(our_database.chatship.all()),
        }

    async def clear(self, chatAction: ChatAction):
        if not chatAction.recv_id:
            return

        oursids = copy.copy(self.id)
        initialize = await self.initialize(chatAction.recv_id)

        our_class = initialize.get("our_class")
        our_frenship = initialize.get("our_frenship")
        our_database = initialize.get("our_database")

        s, our_last_msg_from = self.get_session(oursids, "latest_msgs ", {})

        if our_frenship.friendship_id == chatAction.chatbox and (
            query := our_database.chatship.filter_by(
                friendship=chatAction.chatbox
            ).all()
        ):
            for item in query:
                our_database.session.delete(item)
            our_database.session.commit()

            our_last_msg_from[oursids] = None
            return {
                "__ac": {
                    405: {
                        "__n": f"MJ{chatAction.recv_id}E",
                        "chatBox": chatAction.chatbox,
                    }
                }
            }

    # async def remove(self, recv_id, chatBox, message, timestamp, act):
    async def remove(self, chatAction: ChatAction):
        if not chatAction.recv_id:
            return

        oursids = copy.copy(self.id)
        initialize = await self.initialize(chatAction.recv_id)

        act, message, timestamp = chatAction.payload

        our_class = initialize.get("our_class")
        our_frenship = initialize.get("our_frenship")
        our_database = initialize.get("our_database")

        if our_frenship.friendship_id == chatAction.chatbox:
            query1 = our_database.chatship.filter(
                or_(
                    ChatBoxDatabace.timestamp == timestamp,
                    ChatBoxDatabace.message == message,
                )
            ).first()
            query = {
                "chatBox": chatAction.chatbox,
                "timestamp": timestamp,
                "massid": query1.id,
            }

            our_database.session.delete(query1)
            our_database.session.commit()
            if int(act) == 2:
                recv_class = initialize.get("recv_class")
                recv_database = initialize.get("recv_database")
                query2 = recv_database.chatship.filter(
                    or_(
                        ChatBoxDatabace.timestamp == timestamp,
                        ChatBoxDatabace.message == message,
                    )
                ).first()
                self.add_event(
                    chatAction.recv_id,
                    {
                        "action": "removeMessage",
                        "value": {
                            "chatBox": chatAction.chatbox,
                            "timestamp": timestamp,
                            "massid": query2.id,
                            "__m": f"MJ{chatAction.recv_id}E",
                        },
                    },
                )

                recv_database.session.delete(query2)
                recv_database.session.commit()

            return {"__ac": {402: query}}

        return {
            "our_frenship": str(our_frenship),
            "our_database": str(our_database),
            "our_class": str(our_class),
        }

    async def chacking_session_user_typing(self, status, chatBox):
        oursids = copy.copy(self.id)
        s, query = self.get_session(chatBox, "chatbox", {})
        query = query.setdefault(oursids, {})

        # Compare current status with the new status
        if query.get("status") != status:
            query["status"] = status
            query["lasttime"] = get_adder_timestamp()

    async def onchange_event(self, event):
        oursids = copy.copy(self.id)
        crtimes = get_adder_timestamp()

        def check_timestamp_difference(ts1, ts2, sec=60):
            diff_sec = abs(ts1 - ts2)
            return sec <= diff_sec

        # Get friendships for current member
        database, clss = await get_member_database(oursids)
        friendship = database.friendship.all()

        chatboxs = {}
        our_chatbox_session = None
        for frind in friendship:
            friendship_id = frind.friendship_id

            # Get the session dictionary for this friendship
            s, appchatbox = self.get_session(friendship_id, "chatbox", {})

            # Ensure both member have session data
            our_chatbox_session = appchatbox.setdefault(
                oursids, {"status": 0, "lasttime": crtimes}
            )
            friend_chatbox_session = appchatbox.setdefault(
                frind.second_user, {"status": 0}
            )

            # Check if friend's last activity is more than 10 seconds ago
            if check_timestamp_difference(
                int(friend_chatbox_session.get("lasttime", 0)), crtimes, 6
            ):
                friend_chatbox_session["status"] = 0

            # Check and update own session
            if check_timestamp_difference(
                int(our_chatbox_session.get("lasttime", 0)), crtimes, 5
            ):
                our_chatbox_session["status"] = 1
                our_chatbox_session["lasttime"] = crtimes

            frindStatusList = appchatbox.setdefault(f"FSL_{oursids}", {})
            if (
                frindStatusList.get(frind.second_user)
                != friend_chatbox_session["status"]
            ):
                frindStatusList[frind.second_user] = friend_chatbox_session["status"]
                chatboxs[frind.second_user] = friend_chatbox_session

        data1 = copy.deepcopy(chatboxs)
        mismatched_ids = []
        for key, value in data1.items():
            query = {
                "__m": f"MJ{key}E",
                "_s": value.get("status"),
                "__t": value.get("lasttime"),
            }
            mismatched_ids.append(query)

        # Append the addMessage event to the event list
        if len(mismatched_ids) > 0:
            event.append({"action": "statusUpdate", "value": mismatched_ids})

        return our_chatbox_session

    async def getChatList(self):
        oursids = copy.copy(self.id)

        # Get friendships for current member
        database, table = await get_member_database(oursids)

        friendship = database.friendship.all()

        lastMessage = {}

        for frind in friendship:
            query1 = database.chatship.filter_by(
                friendship=frind.friendship_id
            ).order_by(desc(ChatBoxDatabace.timestamp))
            query2 = query1.filter(ChatBoxDatabace.status == 0).count()
            if query := query1.first():
                """ "the find last message"""
                message = {
                    "__d": query.gettuppel(oursids),
                    "__ms": query.message,
                    "timestamp": query.timestamp,
                    "massid": query.id,
                    "status": query.status,
                    "unred": query2,
                }
                lastMessage[frind.second_user] = message

        # Map secondUsers and create a dict of last_active by member ID
        suser_ids = [f.getFriendId(oursids) for f in friendship]
        ChatBox_ids = {f.getFriendId(oursids): f.friendship_id for f in friendship}

        # Fetch member settings for those IDs
        allfriendli = database.usersetting.filter(
            table.usersetting.id.in_(suser_ids)
        ).all()

        # Create dict for quick lookup: {user_id: last_active}
        last_active_map = {u.id: u for u in allfriendli}

        contern = {}
        for friend in friendship:
            s, chatbox = self.get_session(friend.friendship_id, "chatbox", {})
            chatbox1 = chatbox.setdefault(friend.second_user, {})
            contern[friend.second_user] = chatbox1

        # Callback to add last message
        def callback(data, member):
            if member.id in contern:
                suser_user = contern[member.id]
                # last_active lime
                data["__t"] = suser_user.get("lasttime")

            if member.id in ChatBox_ids:
                chatBox = ChatBox_ids[member.id]
                data["chatBox"] = chatBox

            # data["contern"] = contern
            data["last_message"] = lastMessage.get(member.id)
            return data

        # Get member data with callback
        data = self.member.getIdList(suser_ids, callback)

        return data

    async def getRequestList(self):
        return []

    async def getSearchList(self):
        member = await self.member.getchatdata()
        for item in member:
            id = item["id"]
            chatBox = generate_unique_uuid()

            item["ChatNull"] = True
            item["chatBox"] = chatBox

        return member
