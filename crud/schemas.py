from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSchemaView(BaseModel):
    name: str

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
    chatroom_id: int
    sender: UserSchemaView
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
