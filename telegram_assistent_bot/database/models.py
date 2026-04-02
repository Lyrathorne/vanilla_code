from db import Base
from sqlalchemy import Column, Integer, String,  DateTime
from datetime import datetime, timezone
def get_time():
        current_time = datetime.now(timezone.utc)
        return(current_time)
        

class User(Base):
          __tablename__ = "users"
          id = Column("id", Integer, primary_key=True)
          telegram_id = Column("telegram_id", Integer, unique=True)
          username = Column("username", String, nullable=True)
          first_name = Column("first_name", String)
          created_at = Column("created_at", DateTime, default= get_time)     