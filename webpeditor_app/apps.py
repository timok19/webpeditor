import asyncio

from django.apps import AppConfig
from django_asgi_lifespan.signals import asgi_startup, asgi_shutdown

from webpeditor_app.database.mongodb import MongoDBHandler


class WebpeditorAppConfig(AppConfig):
    name = "webpeditor_app"

    def ready(self):
        asgi_startup.connect(self.sync_mongodb_init)
        asgi_shutdown.connect(self.sync_mongodb_close)

    @staticmethod
    def sync_mongodb_init(*_args, **_kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(MongoDBHandler.mongodb_init())

    @staticmethod
    def sync_mongodb_close(*_args, **_kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(MongoDBHandler.mongodb_close())
