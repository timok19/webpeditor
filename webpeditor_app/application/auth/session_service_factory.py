from typing import Final, final
from django.http import HttpRequest

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.application.auth.session_service import SessionService
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.common.abc.cloudinary_service_abc import CloudinaryServiceABC


@final
class SessionServiceFactory:
    def __init__(
        self,
        user_service: UserServiceABC,
        cloudinary_service: CloudinaryServiceABC,
        logger: WebPEditorLoggerABC,
        editor_repository: EditorRepositoryABC,
        converter_repository: ConverterRepositoryABC,
    ) -> None:
        self.__user_service: Final[UserServiceABC] = user_service
        self.__cloudinary_service: Final[CloudinaryServiceABC] = cloudinary_service
        self.__logger: Final[WebPEditorLoggerABC] = logger
        self.__editor_repository: Final[EditorRepositoryABC] = editor_repository
        self.__converter_repository: Final[ConverterRepositoryABC] = converter_repository

    def create(self, request: HttpRequest) -> SessionService:
        return SessionService(
            request,
            self.__user_service,
            self.__cloudinary_service,
            self.__editor_repository,
            self.__converter_repository,
            self.__logger,
        )
