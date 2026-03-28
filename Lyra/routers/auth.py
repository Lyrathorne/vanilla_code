from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import UserRegister, UserLogin
import services.auth as service

router = APIRouter(prefix="/auth", tags=["auth"])




@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    result = service.register_user(db, user.dict())
    if isinstance(result, dict) and "Error" in result:
        raise HTTPException(status_code=400, detail=result["Error"])
    return result



@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    result = service.login_user(db, user.username, user.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return result