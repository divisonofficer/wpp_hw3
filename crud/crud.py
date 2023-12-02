from sqlalchemy.orm import Session, joinedload, aliased
from crud.models import *
from crud.schemas import *
import datetime


def db_register_user(db: Session, name, passwd):
    db_item = User(name=name, password=passwd, user_info=UserInfo())
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


def insert_message(msg: MessageSchemaBase, db: Session):
    db_item = Message(
        message_type=msg.message_type,
        message=msg.message,
        sender_id=msg.sender_id,
        created_at=datetime.datetime.now(),
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def db_delete_message(db, id, owner_id):
    item = db.query(Message).filter(Message.id == id)
    if item is not None:
        item.delete()
        db.commit()
        return True
    else:
        return False
