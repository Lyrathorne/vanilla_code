from sqlalchemy.orm import Session
from models.user import User
from auth import verify_password, create_access_token
import services.users as user_service


def register_user(db: Session, user_data: dict):
    return user_service.create_user(db, user_data)


def login_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer"
    }