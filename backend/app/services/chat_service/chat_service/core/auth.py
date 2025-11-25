from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
import base64
import json
import hmac
import hashlib
import time
import httpx
from shared.config import settings
from shared.mongo import get_db
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = getattr(settings, "SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
db = get_db()


def _users():
    return db["users"]


def _b64url_decode(s: str) -> bytes:
    s = s.encode() if isinstance(s, str) else s
    padding = b"=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + padding)


def _decode_jwt(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        header = json.loads(_b64url_decode(header_b64))
        payload = json.loads(_b64url_decode(payload_b64))
        if header.get("alg") != ALGORITHM:
            return None
        signing_input = (header_b64 + "." + payload_b64).encode()
        expected = base64.urlsafe_b64encode(hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()).rstrip(b"=")
        if expected.decode() != sig_b64:
            return None
        exp = payload.get("exp")
        if exp and time.time() > float(exp):
            return None
        return payload
    except Exception:
        return None


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Decode locally without external deps
    payload = _decode_jwt(token)
    if payload:
        user_id = payload.get("sub")
        if user_id:
            u = _users().find_one({"_id": ObjectId(user_id)})
            if u:
                return {"id": str(u["_id"]), "email": u.get("email"), "full_name": u.get("full_name"), "created_at": u.get("created_at")}

    # Fallback: validate via user_service /auth/me
    bases = [
        os.getenv("USER_SERVICE_URL"),
        "http://genai_user_service:8086",
        "http://localhost:8001",
        os.getenv("GATEWAY_URL"),
        "http://localhost:8000",
    ]
    for base in [b for b in bases if b]:
        base = base.rstrip("/")
        url = f"{base}/auth/me"
        try:
            with httpx.Client(timeout=10.0) as client:
                r = client.get(url, headers={"Authorization": f"Bearer {token}"})
                if r.status_code == 200:
                    data = r.json()
                    return {"id": data.get("id"), "email": data.get("email"), "full_name": data.get("full_name"), "created_at": data.get("created_at")}
        except Exception:
            pass
    raise credentials_exception
