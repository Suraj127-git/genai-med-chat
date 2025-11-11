from fastapi.testclient import TestClient

from chat_service.main import app


def test_query_basic():
    client = TestClient(app)
    resp = client.post("/api/v1/chat/query", json={"user_id": 1, "text": "Hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)