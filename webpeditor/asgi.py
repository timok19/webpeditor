"""
ASGI config for webpeditor project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django_asgi_lifespan.asgi import get_asgi_application

from reactpy_django import REACTPY_WEBSOCKET_PATH

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webpeditor.settings")

django_asgi_app = get_asgi_application()

protocol_router = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": SessionMiddlewareStack(URLRouter([REACTPY_WEBSOCKET_PATH])),
    }
)


async def application(scope, receive, send):
    await protocol_router(scope, receive, send)
