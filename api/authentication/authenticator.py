from typing import Optional

from django.http import HttpRequest
from ninja_extra.security import AsyncAPIKeyHeader

from api.infrastructure.database.models import APIKey


class APIKeyAuthenticator(AsyncAPIKeyHeader):
    param_name = "X-API-Key"

    async def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        if key is None:
            return None

        hashed_key = APIKey.hash_api_key(key)
        api_key_exist = await APIKey.objects.filter(key_hash=hashed_key).aexists()

        return key if api_key_exist else None
