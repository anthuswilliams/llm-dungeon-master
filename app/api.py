from typing import List
from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI()


class Messages(BaseModel):
    messages: List[str]


@app.get("/")
async def read_index():
    with open("app/frontend/public/index.html", "r") as file:
        content = file.read()
    return Response(content, media_type="text/html")


@app.post("/messages")
async def create_message(messages: Messages):
    return {"messages": messages.messages}
