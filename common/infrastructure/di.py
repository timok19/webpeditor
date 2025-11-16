from anydi import Module, provider

from common.core.abc.logger_abc import LoggerABC
from common.infrastructure.cloudinary.cloudinary_client import CloudinaryClient


class InfrastructureModule(Module):
    @provider(scope="singleton")
    def provide_cloudinary_client(self, logger: LoggerABC) -> CloudinaryClient:
        return CloudinaryClient(logger)
