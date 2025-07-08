from typing import Optional

from django.http import HttpRequest
from ninja_extra.security import AsyncAPIKeyHeader

from webpeditor_app.core.hash_utils import hash_key
from webpeditor_app.infrastructure.database.models.api import APIKey


class APIKeyAuthenticator(AsyncAPIKeyHeader):
    param_name = "X-API-Key"

    async def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        if key is None:
            return None

        key_hash = hash_key(key)
        api_key_exist = await APIKey.objects.filter(key_hash=key_hash).aexists()

        return key if api_key_exist else None
