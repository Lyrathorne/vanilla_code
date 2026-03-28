from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    title: str
    is_group: bool = True
    password: str | None = None


class ChatOut(BaseModel):
    id: int
    title: str
    is_group: bool
    member_ids: list[int]
   

