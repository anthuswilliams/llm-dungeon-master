from typing import List, Dict
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
    messages: List[Dict[str, str]]


@app.post("/messages")
async def create_message(messages: Messages):
    return {"messages": [{"role": msg["role"], "content": msg["content"]} for msg in messages.messages]}
