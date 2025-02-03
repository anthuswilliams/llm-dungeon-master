from typing import List, Dict, Literal
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from utils.elastic import elastic_request, unique_values
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
    model: str
    game: Literal["dnd-5e", "otherscape"]
    knnWeight: float
    keywordWeight: float
    messages: List[Dict[str, str]]


@app.post("/messages")
async def create_message(messages: Messages):
    response = query(messages.messages, knnWeight=messages.knnWeight,
                     keywordWeight=messages.keywordWeight, model=messages.model,
                     game=messages.game)
    return response

@app.get("/games")
async def get_games():
    return unique_values("source-books", "game")
