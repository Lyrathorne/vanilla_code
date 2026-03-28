from pydantic import BaseModel, Field
from typing import List

class ChatCreate(BaseModel):
    title: str
    is_group: bool = True
    member_ids: List[int] = Field(default_factory=list)


class ChatOut(BaseModel):
    id: int
    title: str
    is_group: bool
    member_ids: list[int]
   

