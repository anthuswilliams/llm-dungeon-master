from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI()

from typing import List

class Messages(BaseModel):
    messages: List[str]

@app.get("/")
async def read_index():
    with open("app/frontend/src/index.html", "r") as file:
        content = file.read()
    return Response(content, media_type="text/html")
async def create_message(messages: Messages):
    return {"messages": messages.messages}
