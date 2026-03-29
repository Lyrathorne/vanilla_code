from fastapi import FastAPI
from routers import users, chats, messages, auth
from database import engine, Base
from models import user, chat
from models.user import User
from models.chat import Chat
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(auth.router)
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")


@app.get("/")
def serve_frontend():
    return FileResponse("dist/index.html")

