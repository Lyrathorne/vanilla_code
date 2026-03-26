from fastapi import APIRouter
from schemas.chats import Chat
import services.chats as service

router = APIRouter()

@router.get("/chats")
def get_all_chats():
    return service.get_chats()

@router.get("/chats/{chat_id}")
def get_chat_by_id(chat_id: int):
    chat = service.get_chat(chat_id)
    if chat is None:
        return {"Error": "Chat not found"}
    return chat

@router.post("/chats")
def create_chat(chat: Chat):
    return service.create_chat(chat.dict())

@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: int):
    result = service.delete_chat(chat_id)
    if result is None:
        return {"Error": "Chat not found"}
    return result

@router.post("/chats/{chat_id}/members/{user_id}")
def add_member(chat_id: int, user_id: int):
    return service.add_member(chat_id, user_id)

@router.delete("/chats/{chat_id}/members/{user_id}")
def remove_member(chat_id: int, user_id: int):
    return service.remove_member(chat_id, user_id)