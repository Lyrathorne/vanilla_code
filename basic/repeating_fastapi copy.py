from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

users = [
    {"id": 0, "name": "Alex", "age": 20, "password": "123"},
    {"id": 1, "name": "Bob", "age": 25, "password": "456"}
]

class UserCreate(BaseModel):
    name: str
    age: int
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    age: int

@app.get("/users", response_model=list[UserResponse])
def get_users(min_age: int = None, max_age: int = None):
    for user in users:
        min_age = user.age
        if min_age > user.age:
            min_age = user.age
        return users

@app.get("/users/{id}", response_model=UserResponse)
def get_user_by_id(id: int):
    if id < 0 or id >= len(users):
        raise HTTPException(status_code=404, detail=f"User with id {id} doesn't exist")
    return users[id]

@app.put("/users/{id}", response_model=UserResponse)
def redact_user(id: int, redacted_user: UserCreate):
    if id < 0 or id >= len(users):
        raise HTTPException(status_code=404, detail=f"User with id {id} doesn't exist")

    updated_user = {
        "id": id,
        "name": redacted_user.name,
        "age": redacted_user.age,
        "password": redacted_user.password
    }

    users[id] = updated_user
    return updated_user
