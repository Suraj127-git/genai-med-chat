import os
from cryptography.fernet import Fernet, InvalidToken


def _get_fernet() -> Fernet | None:
    key = os.getenv("MEDICAL_DATA_KEY", "")
    if not key:
        return None
    try:
        return Fernet(key)
    except Exception:
        return None


def encrypt_medical(data: bytes) -> bytes:
    f = _get_fernet()
    if not f:
        return data
    return f.encrypt(data)


def decrypt_medical(token: bytes) -> bytes:
    f = _get_fernet()
    if not f:
        return token
    try:
        return f.decrypt(token)
    except InvalidToken:
        return token

