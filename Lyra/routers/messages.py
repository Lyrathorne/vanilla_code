from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.messages import Message
import services.messages as service
from database import get_db
from fastapi import HTTPException

router = APIRouter()


@router.get("/messages")
def get_all_messages(db: Session = Depends(get_db)):
    return service.get_messages(db)


@router.get("/messages/{message_id}")
def get_message_by_id(message_id: int, db: Session = Depends(get_db)):
    message = service.get_message(db, message_id)
    if message is None:
        
        raise HTTPException(status_code= 404, detail= "Message not found")
    return message


@router.post("/messages")
def create_message(message: Message, db: Session = Depends(get_db)):
    return service.create_message(db, message.dict())


@router.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    result = service.delete_message(db, message_id)
    if result is None:
        raise HTTPException(status_code= 404, detail= "Message not found")
    return result


@router.get("/chats/{chat_id}/messages")
def get_messages_by_chat(chat_id: int, db: Session = Depends(get_db)):
    return service.get_messages_by_chat(db, chat_id)


@router.patch("/messages/{message_id}/read")
def mark_message_as_read(message_id: int, db: Session = Depends(get_db)):
    result = service.mark_as_read(db, message_id)
    if result is None:
        raise HTTPException(status_code= 404, detail= "Message not found")
    return result