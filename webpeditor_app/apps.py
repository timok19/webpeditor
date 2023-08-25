from django.apps import AppConfig
from django_asgi_lifespan.signals import asgi_startup, asgi_shutdown

from webpeditor_app.database.mongodb import MongoDBHandler


class WebpeditorAppConfig(AppConfig):
    name = "webpeditor_app"

    def ready(self):
        asgi_startup.connect(MongoDBHandler.mongodb_init())
        asgi_shutdown.connect(MongoDBHandler.mongodb_close())
