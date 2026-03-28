from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)