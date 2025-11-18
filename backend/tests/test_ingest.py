def test_ingest_upload_requires_file(client):
    resp = client.post("/api/v1/ingest/upload", data={"user_id": 1})
    assert resp.status_code in (400, 422)


def test_ingest_upload_ok(client, tmp_path):
    p = tmp_path / "doc.txt"
    p.write_text("This is a simple test document for ingestion.")
    with p.open("rb") as f:
        resp = client.post(
            "/api/v1/ingest/upload",
            files={"file": ("doc.txt", f, "text/plain")},
            data={"user_id": 1},
        )
    assert resp.status_code in (200, 202)
    j = resp.json()
    assert j.get("status") in ("ingested", "accepted")
    assert "filepath" in j