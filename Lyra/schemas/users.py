from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(min_length=3)
    email: str
    is_active: bool = True
