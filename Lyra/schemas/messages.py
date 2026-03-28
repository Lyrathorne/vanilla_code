from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    chat_id: int
    text: str = Field(min_length=1, max_length=1000)


class MessageOut(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: str
    created_at: str
    is_read: bool

    class Config:
        from_attributes = True
    