"""
Standalone document ingestion script.

Prefers calling the chat_service HTTP API (`/api/v1/ingest/upload`) so we
reuse the microservice code and avoid local heavy deps. Falls back to a simple
local import if needed.

Usage:
  python backend/scripts/ingest_documents.py <filepath> [--user-id 0] [--service-url http://localhost:8003]
"""
import sys
import argparse
import os

def ingest_via_http(file_path: str, user_id: int, service_url: str = "http://localhost:8003"):
    import requests
    url = service_url.rstrip("/") + "/api/v1/ingest/upload"
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        data = {"user_id": str(user_id)}
        r = requests.post(url, files=files, data=data, timeout=60)
        r.raise_for_status()
        print("HTTP ingest response:", r.json())


def ingest_locally(file_path: str, user_id: int):
    # Fallback: try to import the service class from microservices
    try:
        # Add shared path to sys.path dynamically
        base_dir = os.path.dirname(os.path.dirname(__file__))  # backend
        chat_service_dir = os.path.join(base_dir, "microservices-python", "services", "chat_service")
        sys.path.append(chat_service_dir)
        from chat_service.services.ingest_service import IngestService  # type: ignore
        svc = IngestService()
        svc.ingest_file(file_path, uploaded_by=user_id)
        print("Local ingest finished for", file_path)
    except Exception as e:
        print("Local ingest failed:", e)
        print("Please ensure chat_service is running and try HTTP mode.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Path to file for ingestion")
    parser.add_argument("--user-id", type=int, default=0)
    parser.add_argument("--service-url", type=str, default="http://localhost:8003")
    parser.add_argument("--mode", choices=["http", "local"], default="http")
    args = parser.parse_args()

    if args.mode == "http":
        ingest_via_http(args.filepath, args.user_id, args.service_url)
    else:
        ingest_locally(args.filepath, args.user_id)


if __name__ == "__main__":
    main()
