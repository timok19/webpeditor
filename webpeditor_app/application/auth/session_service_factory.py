from typing import Final, final

from django.http import HttpRequest

from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.application.auth.session_service import SessionService
from webpeditor_app.application.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC


@final
class SessionServiceFactory:
    def __init__(
        self,
        user_service: UserServiceABC,
        cloudinary_service: CloudinaryServiceABC,
        logger: WebPEditorLoggerABC,
        editor_repository: EditorRepositoryABC,
        converter_repository: ConverterRepositoryABC,
        user_repository: UserRepositoryABC,
    ) -> None:
        self.__user_service: Final[UserServiceABC] = user_service
        self.__cloudinary_service: Final[CloudinaryServiceABC] = cloudinary_service
        self.__logger: Final[WebPEditorLoggerABC] = logger
        self.__editor_repository: Final[EditorRepositoryABC] = editor_repository
        self.__converter_repository: Final[ConverterRepositoryABC] = converter_repository
        self.__user_repository: Final[UserRepositoryABC] = user_repository

    def create(self, request: HttpRequest) -> SessionService:
        return SessionService(
            request=request,
            user_service=self.__user_service,
            cloudinary_service=self.__cloudinary_service,
            logger=self.__logger,
            editor_repository=self.__editor_repository,
            converter_repository=self.__converter_repository,
            user_repository=self.__user_repository,
        )
