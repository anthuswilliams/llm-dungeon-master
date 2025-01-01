from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

from typing import List

class Messages(BaseModel):
    messages: List[str]

@app.post("/messages")
async def create_message(messages: Messages):
    return {"messages": messages.messages}
