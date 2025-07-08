import secrets
from typing import Any
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create an API key for WebP Editor API's consumer"

    def handle(self, *args: Any, **options: Any) -> None:
        key = secrets.token_hex(32)
        self.stdout.write(self.style.SUCCESS(f"API key '{key}' has been created"))
