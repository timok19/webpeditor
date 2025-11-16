from anydi import Module, provider
from django.http import HttpRequest
from ninja_extra.context import RouteContext

from common.application.abc.filename_utility_abc import FilenameUtilityABC
from common.application.abc.image_file_utility_abc import ImageFileUtilityABC
from common.application.abc.user_service_abc import UserServiceABC
from common.application.abc.validator_abc import ValidatorABC
from common.application.session.session_service_factory import SessionServiceFactory
from common.application.session.user_service import UserService
from common.application.utilities.filename_utility import FilenameUtility
from common.application.utilities.image_file_utility import ImageFileUtility
from common.application.validators.http_request_validator import HttpRequestValidator
from common.application.validators.route_context_validator import RouteContextValidator
from common.core.abc.logger_abc import LoggerABC


class ApplicationModule(Module):
    @provider(scope="request")
    def provide_filename_utility(self, logger: LoggerABC) -> FilenameUtilityABC:
        return FilenameUtility(logger)

    @provider(scope="request")
    def provide_image_file_utility(self, logger: LoggerABC, filename_utility: FilenameUtilityABC) -> ImageFileUtilityABC:
        return ImageFileUtility(logger, filename_utility)

    @provider(scope="request")
    def provide_route_context_validator(self) -> ValidatorABC[RouteContext]:
        return RouteContextValidator()

    @provider(scope="request")
    def provide_http_request_validator(self) -> ValidatorABC[HttpRequest]:
        return HttpRequestValidator()

    @provider(scope="request")
    def provide_user_service(self, logger: LoggerABC) -> UserServiceABC:
        return UserService(logger)

    @provider(scope="request")
    def provide_session_service_factory(self, user_service: UserServiceABC, logger: LoggerABC) -> SessionServiceFactory:
        return SessionServiceFactory(user_service, logger)
