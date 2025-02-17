from django.http import HttpRequest

from webpeditor_app.core.abc.webpeditorlogger import WebPEditorLoggerABC
from webpeditor_app.core.abc.user_service import UserServiceABC
from webpeditor_app.core.auth.session_service import SessionService
from webpeditor_app.domain.abc.converter.queries import ConverterImageAssetQueriesABC
from webpeditor_app.domain.abc.editor.queries import EditorImageAssetsQueriesABC
from webpeditor_app.infrastructure.abc.cloudinary_service import CloudinaryServiceABC


class SessionServiceFactory:
    def __init__(self) -> None:
        from webpeditor_app.common.di_container import DiContainer

        self.__user_service = DiContainer.get_dependency(UserServiceABC)
        self.__cloudinary_service = DiContainer.get_dependency(CloudinaryServiceABC)
        self.__logger = DiContainer.get_dependency(WebPEditorLoggerABC)
        self.__editor_image_assets_queries = DiContainer.get_dependency(EditorImageAssetsQueriesABC)
        self.__converter_image_asset_queries = DiContainer.get_dependency(ConverterImageAssetQueriesABC)

    def create(self, request: HttpRequest) -> SessionService:
        return SessionService(
            request,
            self.__user_service,
            self.__cloudinary_service,
            self.__editor_image_assets_queries,
            self.__converter_image_asset_queries,
            self.__logger,
        )
