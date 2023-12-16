from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import Form


class GroupChatRequest(BaseModel):
    friend_ids: list

    class Config:
        orm_mode = True


class MakeFriendRequest(BaseModel):
    friend_id: int

    class Config:
        orm_mode = True


class UserInfoSchema(BaseModel):
    id: int
    user_id: int
    friends: list

    class Config:
        orm_mode = True
        from_attributes = True


class UserSchemaView(BaseModel):
    id: int
    name: str
    user_info: UserInfoSchema

    class Config:
        orm_mode = True
        from_attributes = True


class UserSchema(BaseModel):
    id: Optional[int]
    name: str
    password: str

    class Config:
        orm_mode = True


class MessageSchemaBase(BaseModel):
    message_type: str
    message: str
    sender_id: int

    class Config:
        orm_mode = True


class MessageSchema(MessageSchemaBase):
    id: Optional[int]
    room_id: int
    sender: UserSchemaView
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
