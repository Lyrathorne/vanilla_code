from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.messages import MessageCreate, MessageOut
import services.messages as service
from database import get_db
from dependencies import get_current_user
from models.user import User

router = APIRouter()


@router.get("/messages", response_model=list[MessageOut])
def get_all_messages(db: Session = Depends(get_db)):
    return service.get_messages(db)


@router.get("/messages/{message_id}", response_model=MessageOut)
def get_message_by_id(message_id: int, db: Session = Depends(get_db)):
    return service.get_message(db, message_id)


@router.post("/messages", response_model=MessageOut)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = message.dict()
    data["sender_id"] = current_user.id
    return service.create_message(db, data)


@router.delete("/messages/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.delete_message(db, message_id)


@router.get("/chats/{chat_id}/messages", response_model=list[MessageOut])
def get_messages_by_chat(chat_id: int, db: Session = Depends(get_db)):
    return service.get_messages_by_chat(db, chat_id)


@router.patch("/messages/{message_id}/read", response_model=MessageOut)
def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.mark_as_read(db, message_id)