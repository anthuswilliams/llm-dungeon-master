from typing import List, Dict, Literal
import os
import magic
from fastapi import FastAPI, Response, UploadFile, File, HTTPException
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


class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str

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

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read the file content
        content = await file.read()
        
        # Check MIME type
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(content)
        
        if file_type != 'application/pdf':
            return UploadResponse(
                filename=file.filename,
                status="error",
                message=f"Only PDF files are accepted. Detected file type: {file_type}"
            )
            
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        return UploadResponse(
            filename=file.filename,
            status="success", 
            message=f"File {file.filename} uploaded successfully"
        )
            
    except Exception as e:
        return UploadResponse(
            filename=file.filename,
            status="error",
            message=f"Error uploading file: {str(e)}"
        )
