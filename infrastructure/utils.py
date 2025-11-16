import hashlib
import secrets


class APIKeyUtils:
    @staticmethod
    def create_api_key() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()
