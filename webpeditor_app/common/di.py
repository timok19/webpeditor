from injector import Module, Binder, threadlocal

from webpeditor_app.common.image_file.image_file_utility_service import ImageFileUtilityService
from webpeditor_app.common.image_file.image_file_utility_service_abc import ImageFileUtilityServiceABC


class DiModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(ImageFileUtilityServiceABC, to=ImageFileUtilityService, scope=threadlocal)
