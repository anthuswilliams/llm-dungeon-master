import pytest
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_create_message():
    response = client.post(
        "/messages",
        json={
            "debug": True,
            "model": "claude-3.5",
            "game": "dnd-5e",
            "knnWeight": 0.4,
            "keywordWeight": 0.6,
            "messages": [{"role": "user", "content": "Hello, world!"}]
        }
    )
    assert response.status_code == 200
    assert "response" in response.json()
