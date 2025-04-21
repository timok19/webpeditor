from dataclasses import dataclass
from typing import final
from django.http import HttpRequest

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.application.auth.session_service import SessionService
from webpeditor_app.infrastructure.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.infrastructure.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.common.abc.cloudinary_service_abc import CloudinaryServiceABC


@final
@dataclass
class SessionServiceFactory:
    user_service: UserServiceABC
    cloudinary_service: CloudinaryServiceABC
    logger: WebPEditorLoggerABC
    editor_queries: EditorQueriesABC
    converter_queries: ConverterQueriesABC

    def create(self, request: HttpRequest) -> SessionService:
        return SessionService(
            request,
            self.user_service,
            self.cloudinary_service,
            self.editor_queries,
            self.converter_queries,
            self.logger,
        )
