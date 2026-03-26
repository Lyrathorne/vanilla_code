from fastapi import APIRouter
import services.users as service
from schemas.users import User
router = APIRouter()
@router.get("/users/search")
def search_users(username: str):
          return service.search_user(username)
@router.get("/users/active")
def get_active():
        return service.search_active()
@router.get("/users")
def get_all_users():
          return service.get_users()
@router.get("/users/{user_id}")
def get_user_by_id(user_id: int):
          user = service.get_user(user_id)
          if user is None:
                    return {"Error": "User not found"}
          return user
@router.post("/users")
def create_user(user: User):
        return service.create_user(user.dict())
@router.put("/users/{user_id}")
def redact_user(user_id : int, new_user : User):
        result = service.redact_user(user_id, new_user.dict())
        if result == None:
                return{"Error" : "this user doesn`t exist"}
        return result
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
          result = service.delete_user(user_id)
          if result is None:
                  return{"Error" : "this user doesn`t exist"}
          return result
        

          