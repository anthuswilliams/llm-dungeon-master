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
    debug: bool
    knn: float
    keywords: float
    messages: List[Dict[str, str]]


@app.post("/messages")
async def create_message(messages: Messages):
    response = query(messages.messages, debug=messages.debug,
                     knn=messages.knn, keywords=messages.keywords)
    if isinstance(response, dict) and "keywords" in response and "context" in response:
        return response
    else:
        return {"response": response}
