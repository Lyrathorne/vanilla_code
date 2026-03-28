from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import services.users as service
from schemas.users import UserCreate, UserUpdate, UserOut
from database import get_db
from dependencies import get_current_user, require_same_user
from models.user import User

router = APIRouter()


@router.get("/users/search", response_model=list[UserOut])
def search_users(username: str, db: Session = Depends(get_db)):
    return service.search_users(db, username)


@router.get("/users/active", response_model=list[UserOut])
def get_active(db: Session = Depends(get_db)):
    return service.search_active(db)


@router.get("/users", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return service.get_users(db)


@router.get("/users/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return service.get_user(db, user_id)


@router.put("/users/{user_id}", response_model=UserOut)
def redact_user(
    user_id: int,
    new_user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_same_user(user_id, current_user)
    return service.redact_user(db, user_id, new_user.dict())


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_same_user(user_id, current_user)
    return service.delete_user(db, user_id)