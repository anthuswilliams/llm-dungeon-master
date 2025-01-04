from typing import List, Dict
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.adjudicator import query

app = FastAPI(root_path="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Messages(BaseModel):
    debug: bool
    knnWeight: float
    keywordWeight: float
    messages: List[Dict[str, str]]


@app.post("/messages")
async def create_message(messages: Messages):
    response = query(messages.messages, knnWeight=messages.knnWeight,
                     keywordWeight=messages.keywordWeight)
    return response
