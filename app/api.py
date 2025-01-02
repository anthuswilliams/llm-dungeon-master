from typing import List
from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI()


class Messages(BaseModel):
    messages: List[str]




@app.post("/messages")
async def create_message(messages: Messages):
    return {"messages": messages.messages}
