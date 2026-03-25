from fastapi import FastAPI
from pydantic import BaseModel
from models.chat import Chat
app = FastAPI()
chat = Chat()
class MessageRequest(BaseModel):
          username: str
          text: str
          
@app.post("/send")
def send_message(data: MessageRequest):
        chat.add_message(data.model_dump())
        return{
          
          "status": "sent"
        }
@app.get("/messages")
def get_messages():
    return chat.get_all_messages()