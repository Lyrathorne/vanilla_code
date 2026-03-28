from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.messages import MessageCreate, MessageOut
import services.messages as service
from database import get_db
from dependencies import get_current_user
from models.user import User
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from websocket_manager import ConnectionManager
from database import SessionLocal
from models.user import User
from auth import decode_access_token
from models.chat import Chat

router = APIRouter()
manager = ConnectionManager()


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
@router.websocket("/ws/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: int, token: str):
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=1008)
        return

    username = payload.get("sub")
    if username is None:
        await websocket.close(code=1008)
        return

    db = SessionLocal()

    try:
        current_user = db.query(User).filter(User.username == username).first()
        if current_user is None:
            await websocket.close(code=1008)
            return

        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat is None:
            await websocket.close(code=1008)
            return

        is_member = False
        for member in chat.members:
            if member.id == current_user.id:
                is_member = True
                break

        if not is_member:
            await websocket.close(code=1008)
            return

        await manager.connect(chat_id, websocket)

        while True:
            text = await websocket.receive_text()

            message_data = {
                "chat_id": chat_id,
                "sender_id": current_user.id,
                "text": text
            }

            saved_message = service.create_message(db, message_data)

            if isinstance(saved_message, dict) and "Error" in saved_message:
                await websocket.send_json(saved_message)
            else:
                await manager.send_message_to_chat(
                    chat_id,
                    {
                        "id": saved_message.id,
                        "chat_id": saved_message.chat_id,
                        "sender_id": saved_message.sender_id,
                        "text": saved_message.text,
                        "created_at": saved_message.created_at,
                        "is_read": saved_message.is_read
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
    finally:
        db.close()