from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=6)
    is_active: bool = True


class UserUpdate(BaseModel):
    username: str = Field(min_length=3)
    email: str
    is_active: bool = True


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True