import anyio
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.controller.llms_controller import router

app = FastAPI()

app.include_router(router)

client = TestClient(app)

def test_sse_chat_tools():
    data = {
        "question": "小浪底水库库容曲线"
    }
    response = client.post("/sse/chat-tools", json=data)
    assert response.status_code == 200


    

if __name__ == "__main__":
    pytest.main()
    # import subprocess
    # subprocess.call(['pytest', '--tb=short', str(__file__)])
    # pytest.main(['./test_sse_chat_tools.py', "--capture=sys", "-W", "ignore:Module already imported:pytest.anyio"])