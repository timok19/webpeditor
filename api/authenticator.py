from typing import Optional

from django.http import HttpRequest
from ninja_extra.security import AsyncAPIKeyHeader

from infrastructure.database.models.api import APIKeyDo
from infrastructure.utils import APIKeyUtils


class APIKeyAuthenticator(AsyncAPIKeyHeader):
    param_name = "X-API-Key"

    async def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        if key is None:
            return None

        key_hash = APIKeyUtils.hash(key)
        api_key_exist = await APIKeyDo.objects.filter(key_hash=key_hash).aexists()

        return key if api_key_exist else None
