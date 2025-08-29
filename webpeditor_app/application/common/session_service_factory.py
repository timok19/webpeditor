from typing import final, Final

from django.http import HttpRequest

from webpeditor_app.application.common.abc.converter_files_repository_abc import ConverterFilesRepositoryABC
from webpeditor_app.application.common.abc.user_service_abc import UserServiceABC
from webpeditor_app.application.common.session_service import SessionService
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC


@final
class SessionServiceFactory:
    def __init__(
        self,
        user_service: UserServiceABC,
        converter_files_repository: ConverterFilesRepositoryABC,
        logger: LoggerABC,
        editor_repository: EditorRepositoryABC,
        converter_repository: ConverterRepositoryABC,
        user_repository: UserRepositoryABC,
    ) -> None:
        self.__user_service: Final[UserServiceABC] = user_service
        self.__converter_files_repository: Final[ConverterFilesRepositoryABC] = converter_files_repository
        self.__logger: Final[LoggerABC] = logger
        self.__editor_repository: Final[EditorRepositoryABC] = editor_repository
        self.__converter_repository: Final[ConverterRepositoryABC] = converter_repository
        self.__user_repository: Final[UserRepositoryABC] = user_repository

    def create(self, request: HttpRequest) -> SessionService:
        return SessionService(
            request=request,
            user_service=self.__user_service,
            converter_files_repo=self.__converter_files_repository,
            logger=self.__logger,
            editor_repo=self.__editor_repository,
            converter_repo=self.__converter_repository,
            user_repo=self.__user_repository,
        )
