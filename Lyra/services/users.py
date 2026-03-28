from sqlalchemy.orm import Session
from models.user import User


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: dict):
    existing_username = db.query(User).filter(User.username == user["username"]).first()
    if existing_username:
        return {"Error": "this name already exists"}

    existing_email = db.query(User).filter(User.email == user["email"]).first()
    if existing_email:
        return {"Error": "Email already exists"}

    db_user = User(
        username=user["username"],
        email=user["email"],
        is_active=user["is_active"]
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def redact_user(db: Session, user_id: int, new_user: dict):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    existing_username = (
        db.query(User)
        .filter(User.username == new_user["username"], User.id != user_id)
        .first()
    )
    if existing_username:
        return {"Error": "this name already exists"}

    existing_email = (
        db.query(User)
        .filter(User.email == new_user["email"], User.id != user_id)
        .first()
    )
    if existing_email:
        return {"Error": "Email already exists"}

    user.username = new_user["username"]
    user.email = new_user["email"]
    user.is_active = new_user["is_active"]

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

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