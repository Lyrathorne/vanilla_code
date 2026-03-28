from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import services.users as service
from schemas.users import User
from database import get_db

router = APIRouter()


@router.get("/users/search")
def search_users(username: str, db: Session = Depends(get_db)):
    return service.search_users(db, username)


@router.get("/users/active")
def get_active(db: Session = Depends(get_db)):
    return service.search_active(db)


@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    return service.get_users(db)


@router.get("/users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = service.get_user(db, user_id)
    if user is None:
        return {"Error": "User not found"}
    return user


@router.post("/users")
def create_user(user: User, db: Session = Depends(get_db)):
    return service.create_user(db, user.dict())


@router.put("/users/{user_id}")
def redact_user(user_id: int, new_user: User, db: Session = Depends(get_db)):
    result = service.redact_user(db, user_id, new_user.dict())
    if result is None:
        return {"Error": "this user doesn`t exist"}
    return result


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    result = service.delete_user(db, user_id)
    if result is None:
        return {"Error": "this user doesn`t exist"}
    return result