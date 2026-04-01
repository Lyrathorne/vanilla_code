from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
Session = async_sessionmaker(
    
    autoflush=False,
    bind=engine,
    class_ = AsyncSession
)

Base = declarative_base()
