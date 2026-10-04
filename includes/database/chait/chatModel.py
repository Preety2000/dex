import uuid
from sqlalchemy import Text, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from includes.database.models.utils import TimeStamp
from includes.database.models.db_exam import JsonList

# Base defined globally for all tables
chatBase = declarative_base()


class FriendShip(chatBase):
    __tablename__ = "friendship"
    first_user = Column(Integer)
    second_user = Column(Integer)
    friendship_id = Column(String)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)
    ChatBoxId = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True
    )

    def getFriendId(self, id):
        return self.second_user if self.first_user == id else self.first_user


class UserSetting(chatBase):
    __tablename__ = "usersetting"
    id = Column(Integer, primary_key=True, unique=True)
    last_active = Column(Integer)
    account_type = Column(Integer)
    last_message = Column(Integer)


class ChatBoxDatabace(chatBase):
    __tablename__ = "chatship"
    id = Column(Integer, primary_key=True)
    zone = Column(Integer, default=0)
    status = Column(Integer, default=0)
    message = Column(Text)
    sender_id = Column(Integer)
    friendship = Column(String(36))
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)

    def gettuppel(self, id):
        return "send" if self.sender_id == id else "resave"


class Sesstion(chatBase):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    data = Column(JsonList)
    timestamp = Column(TimeStamp, default=TimeStamp.now_iso)
