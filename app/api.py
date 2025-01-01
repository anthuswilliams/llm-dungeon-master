from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

from typing import List

class Message(BaseModel):
    content: List[str]
    content: str

@app.post("/messages")
async def create_message(message: Message):
    return {"messages": message.content}
