from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import UserRegister, UserLogin, Token
from schemas.users import UserOut
import services.auth as service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user: UserRegister, db: Session = Depends(get_db)):
    return service.register_user(db, user.dict())


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    result = service.login_user(db, user.username, user.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return result