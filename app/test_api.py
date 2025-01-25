import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.api import app
from utils.elastic import elastic_request

client = TestClient(app)

@patch('utils.elastic.elastic_request')
def test_create_message(mock_elastic_request):
    mock_elastic_request.return_value = {
        "hits": {
            "hits": [
                {"_source": {"content": "Mocked response"}}
            ]
        }
    }
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
