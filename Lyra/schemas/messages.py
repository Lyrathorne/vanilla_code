from pydantic import BaseModel, Field

class Message(BaseModel):
    chat_id: int
    sender_id: int
    text: str = Field(min_length=1, max_length=1000)
    