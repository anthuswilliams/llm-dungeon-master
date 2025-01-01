from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    content: str

@app.post("/messages")
async def create_message(message: Message):
    return {"message": message.content}
