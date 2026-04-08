from database.db import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime


def get_time():
    return datetime.now()


def format_deadline(deadline):
    if deadline is None:
        return "Без дедлайна"

    now = datetime.now()
    delta = deadline - now

    if delta.total_seconds() < 0:
        delta = now - deadline
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"Просрочено на {days}д {hours}ч {minutes}м"

    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    return f"Осталось {days}д {hours}ч {minutes}м"


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True)
    telegram_id = Column("telegram_id", Integer, unique=True)
    username = Column("username", String, nullable=True)
    first_name = Column("first_name", String)
    created_at = Column("created_at", DateTime, default=get_time)
    language = Column("language", String, default="eng" )
    timzone = Column("timezone", String, default="UTC")


class Task(Base):
    __tablename__ = "tasks"

    id = Column("id", Integer, primary_key=True)
    creator_id = Column("creator_id", Integer, ForeignKey("users.id"))
    text = Column("text", String)
    status = Column("status", Boolean, default=False)
    created_at = Column("created_at", DateTime, default=get_time)
    deadline = Column("deadline", DateTime, nullable=True)
    comleted_at = Column("completed_at", DateTime, nullable=True)

    reminded_day = Column("reminded_day", Boolean, default=False)
    reminded_hour = Column("reminded_hour", Boolean, default=False)
    reminded_overdue = Column("reminded_overdue", Boolean, default=False)

class Scheduleitem(Base):
    __tablename__ = "schedule"

    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", Integer, unique=True)
    title = Column("title", String)
    date = Column("date", String)
    start_time = Column("start_time", DateTime)
    end_time = Column("end_time", DateTime)
    location = Column("location", String)
    comment = Column("comment", String)
    created_at = Column("created_at", DateTime)
