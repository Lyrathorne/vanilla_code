from datetime import datetime
from sqlalchemy.orm import Session
from models.message import Message
from models.user import User
from models.chat import Chat
import services.chats as chat_service


def get_messages(db: Session):
    return db.query(Message).all()


def get_message(db: Session, message_id: int):
    return db.query(Message).filter(Message.id == message_id).first()


def create_message(db: Session, message: dict):
    chat = db.query(Chat).filter(Chat.id == message["chat_id"]).first()
    if chat is None:
        return {"Error": "Chat not found"}

    user = db.query(User).filter(User.id == message["sender_id"]).first()
    if user is None:
        return {"Error": "User not found"}

    if not user.is_active:
        return {"Error": "User is offline"}

    

    db_message = Message(
        chat_id=message["chat_id"],
        sender_id=message["sender_id"],
        text=message["text"],
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        is_read=False
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: int):
    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None:
        return None

    db.delete(message)
    db.commit()
    return {"message": "Message deleted"}


def get_messages_by_chat(db: Session, chat_id: int):
    return db.query(Message).filter(Message.chat_id == chat_id).all()


def mark_as_read(db: Session, message_id: int):
    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None:
        return None

    message.is_read = True
    db.commit()
    db.refresh(message)
    return message