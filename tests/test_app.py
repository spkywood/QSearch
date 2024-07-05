import anyio
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api import api_router

app = FastAPI()

app.include_router(api_router)

client = TestClient(app)

def test_sse_chat_tools():
    data = {
        "question": "小浪底水库库容曲线"
    }
    response = client.post("/sse/chat-tools", json=data)
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main()