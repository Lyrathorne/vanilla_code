from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user import User
from auth import hash_password


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_username(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def create_user(db: Session, user: dict):
    existing_username = db.query(User).filter(User.username == user["username"]).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="This name already exists")

    existing_email = db.query(User).filter(User.email == user["email"]).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    db_user = User(
        username=user["username"],
        email=user["email"],
        is_active=user.get("is_active", True),
        hashed_password=hash_password(user["password"])
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def redact_user(db: Session, user_id: int, new_user: dict):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    existing_username = (
        db.query(User)
        .filter(User.username == new_user["username"], User.id != user_id)
        .first()
    )
    if existing_username:
        raise HTTPException(status_code=400, detail="This name already exists")

    existing_email = (
        db.query(User)
        .filter(User.email == new_user["email"], User.id != user_id)
        .first()
    )
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    user.username = new_user["username"]
    user.email = new_user["email"]
    user.is_active = new_user["is_active"]

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


def search_users(db: Session, username: str):
    all_users = db.query(User).all()
    results = []

    for user in all_users:
        if username.lower() in user.username.lower():
            results.append(user)

    return results


def search_active(db: Session):
    return db.query(User).filter(User.is_active == True).all()