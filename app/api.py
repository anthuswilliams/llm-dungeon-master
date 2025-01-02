from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

from typing import List, Dict

class Messages(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/messages")
async def create_message(messages: Messages):
    return {"messages": [{"role": msg["role"], "content": msg["content"]} for msg in messages.messages]}
