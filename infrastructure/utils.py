import hashlib
import secrets


class APIKeyUtils:
    @staticmethod
    def create() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()
