from typing import Final, final
from django.http import HttpRequest

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.application.auth.session_service import SessionService
from webpeditor_app.infrastructure.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.infrastructure.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.infrastructure.abc.cloudinary_service_abc import CloudinaryServiceABC


@final
class SessionServiceFactory:
    def __init__(self) -> None:
        from webpeditor_app.core.di_container import DiContainer

        self.__user_service: Final[UserServiceABC] = DiContainer.get_dependency(UserServiceABC)
        self.__cloudinary_service: Final[CloudinaryServiceABC] = DiContainer.get_dependency(CloudinaryServiceABC)
        self.__logger: Final[WebPEditorLoggerABC] = DiContainer.get_dependency(WebPEditorLoggerABC)
        self.__editor_queries: Final[EditorQueriesABC] = DiContainer.get_dependency(EditorQueriesABC)
        self.__converter_queries: Final[ConverterQueriesABC] = DiContainer.get_dependency(ConverterQueriesABC)

    def create(self, request: HttpRequest) -> SessionService:
        return SessionService(
            request,
            self.__user_service,
            self.__cloudinary_service,
            self.__editor_queries,
            self.__converter_queries,
            self.__logger,
        )
