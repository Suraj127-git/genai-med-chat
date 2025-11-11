def test_voice_requires_file(client):
    resp = client.post("/api/v1/voice")
    # UploadFile is required, FastAPI will return 422
    assert resp.status_code == 422