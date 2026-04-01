from db import Base
from sqlalchemy import Column, Integer, String,  DateTime
from datetime import datetime

class User(Base):
          __tablename__ = "users"
          id = Column("id", Integer, primary_key=True)
          telegram_id = Column("telegram_id", Integer)
          username = Column("username", String, nullable=True)
          first_name = Column("first_name", String)
          created_at = Column("created_at", DateTime)     