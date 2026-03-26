from fastapi import FastAPI
from routers import users, chats, messages

app = FastAPI()

app.include_router(users.router)
app.include_router(chats.router)
app.include_router(messages.router)