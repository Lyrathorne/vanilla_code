from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import UserRegister, Token
from schemas.users import UserOut
import services.auth as service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user: UserRegister, db: Session = Depends(get_db)):
    return service.register_user(db, user.dict())


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    result = service.login_user(db, form_data.username, form_data.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return result