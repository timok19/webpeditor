import hashlib
import secrets


def create_api_key() -> str:
    return secrets.token_urlsafe(32)


def create_api_key_hash(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()
