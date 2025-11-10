def test_graph_returns_structure(client):
    r = client.post("/api/v1/chat/query", json={"user_id": 2, "text": "Tell me about diabetes"})
    assert r.status_code == 200
    conv_id = r.json().get("conv_id")
    assert conv_id is not None

    resp = client.get(f"/api/v1/graph/{conv_id}")
    assert resp.status_code == 200
    graph = resp.json()
    assert isinstance(graph.get("nodes"), list)
    assert isinstance(graph.get("edges"), list)