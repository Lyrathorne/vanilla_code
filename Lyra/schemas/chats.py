from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    is_group: bool
    member_ids: list[int]


class ChatOut(BaseModel):
    id: int
    title: str
    is_group: bool
    member_ids: list[int]