from pydantic import BaseModel, Field

class Chat(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    is_group: bool
    member_ids: list[int]