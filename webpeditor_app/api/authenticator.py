from typing import Optional

from django.http import HttpRequest
from ninja.security import APIKeyHeader

from webpeditor import settings


class APIKeyAuthenticator(APIKeyHeader):
    # TODO: create a separate app for creating API keys (storing the database and hashing values)
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        return key if key == settings.WEBPEDITOR_API_KEY else None
