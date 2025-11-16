from typing import Optional

from django.http import HttpRequest
from ninja_extra.security import AsyncAPIKeyHeader

from infrastructure.database.models.api import APIKey
from infrastructure.utils import APIKeyUtils


class APIKeyAuthenticator(AsyncAPIKeyHeader):
    param_name = "X-API-Key"

    async def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        if key is None:
            return None

        hashed_key = APIKeyUtils.hash(key)
        api_key_exist = await APIKey.objects.filter(key_hash=hashed_key).aexists()

        return key if api_key_exist else None
