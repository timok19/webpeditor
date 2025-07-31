import hashlib
from typing import Optional

from django.http import HttpRequest
from ninja_extra.security import AsyncAPIKeyHeader

from webpeditor_app.infrastructure.database.models.api import APIKey


class APIKeyAuthenticator(AsyncAPIKeyHeader):
    param_name = "X-API-Key"

    async def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        if key is None:
            return None

        hashed_key = self.__hash_key(key)
        api_key_exist = await APIKey.objects.filter(key_hash=hashed_key).aexists()

        return key if api_key_exist else None

    @staticmethod
    def __hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode()).hexdigest()
