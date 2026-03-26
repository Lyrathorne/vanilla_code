from fastapi import APIRouter
from schemas.messages import Message
import services.messages as service

router = APIRouter()

@router.get("/messages")
def get_all_messages():
    return service.get_messages()

@router.get("/messages/{message_id}")
def get_message_by_id(message_id: int):
    message = service.get_message(message_id)
    if message is None:
        return {"Error": "Message not found"}
    return message

@router.post("/messages")
def create_message(message: Message):
    return service.create_message(message.dict())

@router.delete("/messages/{message_id}")
def delete_message(message_id: int):
    result = service.delete_message(message_id)
    if result is None:
        return {"Error": "Message not found"}
    return result

@router.get("/chats/{chat_id}/messages")
def get_messages_by_chat(chat_id: int):
    return service.get_messages_by_chat(chat_id)

@router.patch("/messages/{message_id}/read")
def mark_message_as_read(message_id: int):
    result = service.mark_as_read(message_id)
    if result is None:
        return {"Error": "Message not found"}
    return result