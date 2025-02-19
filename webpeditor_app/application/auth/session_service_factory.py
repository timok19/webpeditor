from typing import Final
from django.http import HttpRequest

from webpeditor_app.core.abc.webpeditorlogger import WebPEditorLoggerABC
from webpeditor_app.application.auth.abc.user_service import UserServiceABC
from webpeditor_app.application.auth.session_service import SessionService
from webpeditor_app.domain.abc.converter.queries import ConverterQueriesABC
from webpeditor_app.domain.abc.editor.queries import EditorQueriesABC
from webpeditor_app.infrastructure.abc.cloudinary_service import CloudinaryServiceABC


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
