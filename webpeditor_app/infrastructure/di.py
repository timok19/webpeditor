from injector import Module, Binder, singleton

from webpeditor_app.infrastructure.cloudinary.cloudinary_service import CloudinaryService
from webpeditor_app.infrastructure.cloudinary.cloudinary_service_abc import CloudinaryServiceABC


class DiModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(CloudinaryServiceABC, to=CloudinaryService, scope=singleton)
