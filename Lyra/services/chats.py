from sqlalchemy.orm import Session
from models.chat import Chat
from models.user import User
from fastapi import HTTPException





def get_chats(db: Session):
    return db.query(Chat).all()


def get_chat(db: Session, chat_id: int):
    return db.query(Chat).filter(Chat.id == chat_id).first()


def user_exists(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    return user is not None


def get_chats(db: Session):
    return db.query(Chat).all()


def get_chat(db: Session, chat_id: int):
    return db.query(Chat).filter(Chat.id == chat_id).first()


def create_chat(db: Session, chat: dict):
    if not chat["member_ids"]:
        raise HTTPException(status_code= 403, detail= "Chat must have members")

    members = []
    for user_id in chat["member_ids"]:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            
            raise HTTPException(status_code= 404, detail= f"User with id {user_id} not found")
        members.append(user)

    if not chat["is_group"] and len(members) != 2:
        
        raise HTTPException(status_code= 403, detail= "Private chat must have exactly 2 members")

    db_chat = Chat(
        title=chat["title"],
        is_group=chat["is_group"]
    )

    db_chat.members = members

    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)

    return {
        "id": db_chat.id,
        "title": db_chat.title,
        "is_group": db_chat.is_group,
        "member_ids": [member.id for member in db_chat.members]
    }


def delete_chat(db: Session, chat_id: int):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat is None:
        return None

    db.delete(chat)
    db.commit()

    

    return {"message": "Chat deleted"}


def add_member(db: Session, chat_id: int, user_id: int):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat is None:
        
        raise HTTPException(status_code= 404, detail= "Chat not found")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        
        raise HTTPException(status_code= 404, detail= "User not found")

    if not chat.is_group:
       
        raise HTTPException(status_code= 403, detail= "Cannot change members in private chat")

    if user in chat.members:
        
        raise HTTPException(status_code= 400, detail= "User already in chat")

    chat.members.append(user)
    db.commit()
    db.refresh(chat)

    return {
        "id": chat.id,
        "title": chat.title,
        "is_group": chat.is_group,
        "member_ids": [member.id for member in chat.members]
    }


def remove_member(db: Session, chat_id: int, user_id: int):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat is None:
        raise HTTPException(status_code= 404, detail= "Chat not found")

    if not chat.is_group:
        raise HTTPException(status_code= 403, detail= "Cannot change members in private chat")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code= 404, detail= "User not found")

    if user not in chat.members:
        raise HTTPException(status_code= 400, detail= "User is not in chat")

    chat.members.remove(user)
    db.commit()
    db.refresh(chat)

    return {
        "id": chat.id,
        "title": chat.title,
        "is_group": chat.is_group,
        "member_ids": [member.id for member in chat.members]
    }


def get_chat_with_members(db: Session, chat_id: int):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat is None:
        return None

    return {
        "id": chat.id,
        "title": chat.title,
        "is_group": chat.is_group,
        "member_ids": [member.id for member in chat.members]
    }


def get_all_chats_with_members(db: Session):
    chats = db.query(Chat).all()
    result = []

    for chat in chats:
        result.append({
            "id": chat.id,
            "title": chat.title,
            "is_group": chat.is_group,
            "member_ids": [member.id for member in chat.members]
        })

    return result