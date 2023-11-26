from sqlalchemy.orm import Session, joinedload
from crud.models import User, Message, Base
from crud.schemas import MessageSchemaBase
import datetime
def db_register_user(db: Session, name, passwd):
    db_item = User(name=name, password=passwd)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def read_user(db: Session, name, passwrd):
    return db.query(User).filter(User.name == name).first()

def read_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()

def read_all_messages(db: Session):
    return db.query(Message).options(joinedload(Message.sender)).all()

def insert_message(msg: MessageSchemaBase, db: Session):
    db_item = Message(message_type=msg.message_type, message=msg.message, sender_id=msg.sender_id,
                      created_at=datetime.datetime.now()   
                        )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def db_delete_message(
        db,
        id,
        owner_id
    ):
    item = db.query(Message).filter(Message.id == id)
    if item is not None:
        item.delete()
        db.commit()
        return True
    else:
        return False