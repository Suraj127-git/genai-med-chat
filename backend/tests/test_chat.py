def test_chat_query_success(client):
    resp = client.post("/api/v1/chat/query", json={"user_id": 1, "text": "Hello world"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("answer"), str)
    assert data.get("conv_id") is not None


def test_chat_query_missing_text(client):
    resp = client.post("/api/v1/chat/query", json={"user_id": 1, "text": ""})
    assert resp.status_code == 400