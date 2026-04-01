from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
users = []
class UserCreate(BaseModel):
          name : str
          age : int
class UserResponse(BaseModel):
        id : int
        name : str
        age : int
app.get("/users")
def get_all_users():
        return users
app.post("/users")
def create_user(user : UserCreate):
        new_user = {
          "id": len(users) + 1,
          "name": user.name,
          "age": user.age
        }
        users.append(new_user)
        return(users)
app.get("/users/{id}")
def get_one_user(id : int):
        return users[id]