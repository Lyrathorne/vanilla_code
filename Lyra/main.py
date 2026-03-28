from fastapi import FastAPI
from routers import users, chats, messages
from database import engine, Base
from Lyra.models import user
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(user.router)
app.include_router(chats.router)
app.include_router(messages.router)
