from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship

from crud.database import Base

# Association table for the many-to-many relationship between Users
friends_association = Table(
    "friends_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("friend_id", Integer, ForeignKey("users.id")),
)
# Association table for the many-to-many relationship between Users and ChatRooms

chatroom_association = Table(
    "chatroom_association",
    Base.metadata,
    Column("chat_room_id", Integer, ForeignKey("chat_rooms.id")),
    Column("user_id", Integer, ForeignKey("user_info.user_id")),
)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    # Relationship to find the chatroom of the message
    room = relationship("ChatRoom", back_populates="messages")
    message_type = Column(String)
    message = Column(String)
    sender_id = Column(Integer, ForeignKey("users.id"))
    # Relationship to find the sender of the message
    sender = relationship("User", foreign_keys=[sender_id])
    created_at = Column(DateTime)


class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime)
    user_count = Column(Integer)
    # Relationship for users
    user_infos = relationship(
        "UserInfo", secondary=chatroom_association, back_populates="chatrooms"
    )
    user_chatroom_info = relationship("UserChatroomInfo", back_populates="chatroom")
    # Relationship for messages
    messages = relationship("Message", back_populates="room")


class UserChatroomInfo(Base):
    __tablename__ = "user_chatroom_info"
    chatroom_id = Column(Integer, ForeignKey("chat_rooms.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user_info.user_id"), primary_key=True)
    display_name = Column(String)
    unread_message_count = Column(Integer)
    chatroom = relationship("ChatRoom", back_populates="user_chatroom_info")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    password = Column(String)
    created_at = Column(DateTime)
    # One-to-one relationship with UserInfo
    user_info = relationship("UserInfo", back_populates="user", uselist=False)

    def hide_password(self):
        self.password = None
        return self


class UserInfo(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String)
    # Additional user information fields (if any)
    # Relationship for friends
    friends = relationship(
        "UserInfo",
        secondary=friends_association,
        primaryjoin=id == friends_association.c.user_id,
        secondaryjoin=id == friends_association.c.friend_id,
    )
    # Relationship for chatrooms
    chatrooms = relationship(
        "ChatRoom", secondary=chatroom_association, back_populates="user_infos"
    )
    # Relationship for ProfileImage
    profile_image = relationship(
        "ProfileImage", back_populates="user_info", uselist=False
    )
    # Back reference to User
    user = relationship("User", back_populates="user_info")


class ProfileImage(Base):
    __tablename__ = "profile_images"
    id = Column(Integer, primary_key=True, index=True)
    user_info_id = Column(Integer, ForeignKey("user_info.id"))
    image_file_path = Column(String)
    # Back reference to UserInfo
    user_info = relationship("UserInfo", back_populates="profile_image")
