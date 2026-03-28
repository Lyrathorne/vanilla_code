from fastapi import FastAPI
from routers import users, chats, messages, auth
from database import engine, Base
from models import user
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(users.router)
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(auth.router)
