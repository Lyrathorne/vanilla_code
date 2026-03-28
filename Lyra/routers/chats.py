from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.chats import Chat
import services.chats as service
from database import get_db

router = APIRouter()


@router.get("/chats")
def get_all_chats(db: Session = Depends(get_db)):
    return service.get_all_chats_with_members(db)


@router.get("/chats/{chat_id}")
def get_chat_by_id(chat_id: int, db: Session = Depends(get_db)):
    chat = service.get_chat_with_members(db, chat_id)
    if chat is None:
        return {"Error": "Chat not found"}
    return chat


@router.post("/chats")
def create_chat(chat: Chat, db: Session = Depends(get_db)):
    return service.create_chat(db, chat.dict())


@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    result = service.delete_chat(db, chat_id)
    if result is None:
        return {"Error": "Chat not found"}
    return result


@router.post("/chats/{chat_id}/members/{user_id}")
def add_member(chat_id: int, user_id: int, db: Session = Depends(get_db)):
    return service.add_member(db, chat_id, user_id)


@router.delete("/chats/{chat_id}/members/{user_id}")
def remove_member(chat_id: int, user_id: int, db: Session = Depends(get_db)):
    return service.remove_member(db, chat_id, user_id)