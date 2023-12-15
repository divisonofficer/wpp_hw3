from sqlalchemy.orm import Session, joinedload, aliased
from crud.models import *
from sqlalchemy import func
from crud.schemas import *
import datetime
import logging

logger = logging.getLogger(__name__)


def db_register_user(db: Session, name, passwd):
    user_info = UserInfo()
    user_info.user_name = name
    db_item = User(name=name, password=passwd, user_info=user_info)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def read_user(db: Session, name, passwrd):
    return (
        db.query(User)
        .filter(User.name == name)
        .filter(User.password == passwrd)
        .options(joinedload(User.user_info))
        .first()
        .hide_password()
    )


def read_user_by_id(db: Session, id: int):
    return (
        db.query(User)
        .filter(User.id == id)
        .options(joinedload(User.user_info))
        .first()
        .hide_password()
    )


def read_friends(db: Session, user_id: int):
    return [
        user.hide_password()
        for user in (
            db.query(User)
            .join(UserInfo, User.id == UserInfo.user_id)
            .join(friends_association, UserInfo.id == friends_association.c.friend_id)
            .filter(friends_association.c.user_id == user_id)
            .options(joinedload(User.user_info))
            .all()
        )
    ]


def read_candidate_friends(db: Session, target_user_id: int):
    """
    return user who is not friend of userId
    friend is defined in user_info table
    """
    # User ID for which we want to find non-friends

    # Alias for user_info to distinguish between user and friend in the join
    friend_info = aliased(UserInfo)
    # Subquery to find all friends of the target user
    subquery = (
        db.query(friend_info.user_id)
        .join(friends_association, friend_info.id == friends_association.c.friend_id)
        .filter(friends_association.c.user_id == target_user_id)
        .subquery()
    )

    # Main query to find users who are not friends of the target user
    non_friends = (
        db.query(User)
        .join(UserInfo, User.id == UserInfo.user_id)
        .filter(~(UserInfo.user_id.in_(subquery)))
    )

    # Execute the query
    return [
        user.hide_password()
        for user in (
            non_friends.filter(User.id != target_user_id)
            .options(joinedload(User.user_info))
            .all()
        )
    ]


def make_friend(db: Session, user_id: int, friend_id: int):
    if user_id == friend_id:
        return None
    if db.query(User.id == friend_id).all() is None:
        return None

    if (
        db.query(friends_association)
        .filter(friends_association.c.user_id == user_id)
        .filter(friends_association.c.friend_id == friend_id)
        .first()
        is not None
    ):
        return None
    db_item = friends_association.insert().values(user_id=user_id, friend_id=friend_id)
    db.execute(db_item)
    db.commit()


def read_all_messages(db: Session):
    return db.query(Message).options(joinedload(Message.sender)).all()


def read_chatroom_message(db: Session, chatroom_id: int):
    return (
        db.query(Message)
        .filter(Message.room_id == chatroom_id)
        .options(joinedload(Message.sender))
        .all()
    )


def insert_message(msg: MessageSchemaBase, room_id: int, db: Session):
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    db_item = Message(
        message_type=msg.message_type,
        message=msg.message,
        sender_id=msg.sender_id,
        room_id=room_id,
        # room=room,
        created_at=datetime.datetime.now(),
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    sender = db.query(User).filter(User.id == msg.sender_id).first()

    return {
        "id": db_item.id,
        "message_type": db_item.message_type,
        "message": db_item.message,
        "sender": {
            "id": sender.id,
            "name": sender.name,
        },
        "created_at": db_item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "sender_id": db_item.sender_id,
        "room_id": db_item.room_id,
    }


def db_delete_message(db, id, owner_id):
    item = db.query(Message).filter(Message.id == id)
    if item is not None:
        item.delete()
        db.commit()
        return True
    else:
        return False


def getP2PChatRoomInfo(db: Session, user_id, friend_id):
    """
    get chatrooms which contains only two users, user_id and friend_id in Chatroom.user_infos
    length of user_infos should be 2
    """
    chatroom = (
        db.query(ChatRoom)
        .filter(ChatRoom.user_infos.any(id=user_id))
        .filter(ChatRoom.user_infos.any(id=friend_id))
        .first()
    )
    if chatroom is None:
        chatroom = createChatroom(db, [user_id, friend_id])

    return chatroom


def createChatroom(db: Session, user_ids: list):
    """
    create chatroom with user_ids
    """
    db_item = ChatRoom(
        name="",
        created_at=datetime.datetime.now(),
        user_count=len(user_ids),
    )
    db.add(db_item)
    db.commit()
    name = ""
    users = []
    for user_id in user_ids:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .options(joinedload(User.user_info))
            .first()
        )
        db_item.user_infos.append(user.user_info)
        users.append(
            {
                "id": user.id,
                "name": user.name,
            }
        )
        name += user.name + ", "
    db_item.name = name

    db.refresh(db_item)
    db.commit()

    for user_id in user_ids:
        # find user where user['user_id'] == user_id in users

        user = next((user for user in users if user["id"] != user_id), None)
        user_chatroom_info = UserChatroomInfo(
            chatroom_id=db_item.id,
            user_id=user_id,
            unread_message_count=0,
            display_name=len(user_ids) == 2 and user["name"] or name,
        )
        logger.debug(user_chatroom_info)
        db.add(user_chatroom_info)
        db.commit()

    return (
        db.query(ChatRoom)
        .filter(ChatRoom.id == db_item.id)
        .options(joinedload(ChatRoom.user_infos))
        .first()
    )


def read_user_chatroom_all(db: Session, user_id: int):
    """
    get all chatrooms which contains user_id
    include each chatroom's latest message
    """
    subquery = (
        db.query(Message.room_id, func.max(Message.created_at).label("latest"))
        .group_by(Message.room_id)
        .subquery("latest_message_subquery")
    )

    # Aliased Message for joining
    latest_message = aliased(Message)

    # Query all chat rooms and join with the subquery to get the latest message
    chat_rooms = (
        db.query(UserChatroomInfo)
        .filter(UserChatroomInfo.user_id == user_id)
        .options(joinedload(UserChatroomInfo.chatroom))
        .all()
    )
    return [
        {
            "chat_room": chat_room,
            "latest_message": db.query(Message)
            .filter(Message.room_id == chat_room.chatroom_id)
            .order_by(Message.created_at.desc())
            .first(),
        }
        for chat_room in chat_rooms
    ]


def removeChatroom(db: Session, roomId: int):
    """
    remove chatroom with roomId
    """
    db_item = (
        db.query(ChatRoom)
        .filter(ChatRoom.id == roomId)
        .options(joinedload(ChatRoom.messages))
        .options(joinedload(ChatRoom.user_chatroom_info))
        .first()
    )
    if db_item is not None:
        for user_info in db_item.user_chatroom_info:
            db.delete(user_info)

        for message in db_item.messages:
            db.delete(message)

        db.delete(db_item)

        db.commit()
        return True
    else:
        return False
