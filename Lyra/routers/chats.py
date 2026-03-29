from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.chats import ChatCreate, ChatOut
import services.chats as service
from database import get_db
from dependencies import get_current_user
from models.user import User

router = APIRouter()


@router.get("/chats", response_model=list[ChatOut])
def get_all_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_all_chats_with_members(db, current_user.id)


@router.get("/chats/{chat_id}", response_model=ChatOut)
def get_chat_by_id(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_chat_with_members(db, chat_id, current_user.id)


@router.post("/chats", response_model=ChatOut)
def create_chat(
    data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat_data = data.model_dump()

    if current_user.id not in chat_data["member_ids"]:
        chat_data["member_ids"].append(current_user.id)

    return service.create_chat(db, chat_data)


@router.delete("/chats/{chat_id}")
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.delete_chat(db, chat_id, current_user.id)


@router.post("/chats/{chat_id}/members/{user_id}", response_model=ChatOut)
def add_member(
    chat_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.add_member(db, chat_id, user_id, current_user.id)


@router.delete("/chats/{chat_id}/members/{user_id}", response_model=ChatOut)
def remove_member(
    chat_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.remove_member(db, chat_id, user_id, current_user.id)