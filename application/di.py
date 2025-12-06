from typing import Annotated

from anydi import Module, provider

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.common.abc.signing_service_abc import SigningServiceABC
from application.common.abc.validator_abc import ValidatorABC
from application.common.services.session_service_factory import SessionServiceFactory
from application.common.services.signing_service import SigningService
from application.common.services.filename_service import FilenameService
from application.common.services.image_file_service import ImageFileService
from application.converter.commands.convert_images_command import ConvertImagesCommand
from application.converter.commands.schemas import ConversionRequest
from application.converter.queries.get_converted_zip_query import GetConvertedZipQuery
from application.converter.services.abc.image_file_converter_abc import ImageFileConverterABC
from application.converter.services.image_file_converter import ImageFileConverter
from application.converter.validators.conversion_request_validator import ConversionRequestValidator
from core.abc.logger_abc import LoggerABC
from infrastructure.abc.converter_image_assets_repository_abc import ConverterImageAssetsRepositoryABC
from infrastructure.abc.files_repository_abc import FilesRepositoryABC
from infrastructure.repositories.converter_files.converter_files_repository import ConverterFilesRepository


class ApplicationModule(Module):
    @provider(scope="request")
    def provide_filename_service(self, logger: LoggerABC) -> FilenameServiceABC:
        return FilenameService(logger)

    @provider(scope="request")
    def provide_image_file_service(self, logger: LoggerABC, filename_service: FilenameServiceABC) -> ImageFileServiceABC:
        return ImageFileService(logger, filename_service)

    @provider(scope="request")
    def provide_signing_service(self, logger: LoggerABC) -> SigningServiceABC:
        return SigningService(logger)

    @provider(scope="request")
    def provide_session_service_factory(self, signing_service: SigningServiceABC, logger: LoggerABC) -> SessionServiceFactory:
        return SessionServiceFactory(signing_service, logger)

    @provider(scope="request")
    def provide_conversion_request_validator(
        self,
        image_file_service: ImageFileServiceABC,
        filename_service: FilenameServiceABC,
        logger: LoggerABC,
    ) -> ValidatorABC[ConversionRequest]:
        return ConversionRequestValidator(image_file_service, filename_service, logger)

    @provider(scope="request")
    def provide_converter_service(
        self,
        image_file_service: ImageFileServiceABC,
        filename_service: FilenameServiceABC,
        logger: LoggerABC,
    ) -> ImageFileConverterABC:
        return ImageFileConverter(image_file_service, filename_service, logger)

    @provider(scope="request")
    def provide_convert_images_command(
        self,
        session_service_factory: SessionServiceFactory,
        conversion_request_validator: ValidatorABC[ConversionRequest],
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        image_converter: ImageFileConverterABC,
        image_file_service: ImageFileServiceABC,
        filename_service: FilenameServiceABC,
        converter_repo: ConverterImageAssetsRepositoryABC,
        logger: LoggerABC,
    ) -> ConvertImagesCommand:
        return ConvertImagesCommand(
            session_service_factory,
            conversion_request_validator,
            converter_files_repo,
            image_converter,
            image_file_service,
            filename_service,
            converter_repo,
            logger,
        )

    @provider(scope="request")
    def provide_get_zip_query(
        self,
        session_service_factory: SessionServiceFactory,
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        converter_repo: ConverterImageAssetsRepositoryABC,
    ) -> GetConvertedZipQuery:
        return GetConvertedZipQuery(session_service_factory, converter_files_repo, converter_repo)
