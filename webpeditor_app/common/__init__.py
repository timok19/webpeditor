from anydi import Module, provider

from webpeditor_app.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.cloudinary.cloudinary_service import CloudinaryService
from webpeditor_app.common.image_file.image_file_utility import ImageFileUtility
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient


class CommonModule(Module):
    @provider(scope="request")
    def image_file_utility_provider(self, logger: WebPEditorLoggerABC) -> ImageFileUtilityABC:
        return ImageFileUtility(logger=logger)

    @provider(scope="singleton")
    def cloudinary_service_provider(
        self,
        cloudinary_client: CloudinaryClient,
        logger: WebPEditorLoggerABC,
    ) -> CloudinaryServiceABC:
        return CloudinaryService(cloudinary_client=cloudinary_client, logger=logger)
