from abc import ABC, abstractmethod
from rest_framework.request import Request

from webpeditor_app.core.auth.session import SessionService


class SessionServiceFactoryABC(ABC):
    @abstractmethod
    def create(self, request: Request) -> SessionService: ...
