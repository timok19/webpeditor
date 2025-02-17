"""
ASGI config for webpeditor project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from webpeditor_app.common.di_container import DiContainer

from django.core.asgi import get_asgi_application
from django.core.handlers.asgi import ASGIHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webpeditor.settings")

DiContainer.create()

application: ASGIHandler = get_asgi_application()
