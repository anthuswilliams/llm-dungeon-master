from typing import List
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.adjudicator import query

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Messages(BaseModel):
    messages: List[str]


@app.post("/messages")
async def create_message(messages: Messages):
    responses = [query(message) for message in messages.messages]
    return {"responses": responses}
