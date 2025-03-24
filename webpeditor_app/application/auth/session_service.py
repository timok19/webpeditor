import math
from datetime import timedelta
from typing import Final, final

from django.http.request import HttpRequest
from django.utils import timezone
from expression import Option

from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.context_result import ContextResult, ErrorContext
from webpeditor_app.infrastructure.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.infrastructure.database.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.infrastructure.database.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.models.app_user import AppUser


@final
class SessionService:
    def __init__(
        self,
        request: HttpRequest,
        user_service: UserServiceABC,
        cloudinary_service: CloudinaryServiceABC,
        editor_queries: EditorQueriesABC,
        converter_queries: ConverterQueriesABC,
        logger: WebPEditorLoggerABC,
    ) -> None:
        self.__request: Final[HttpRequest] = request
        self.__user_service: Final[UserServiceABC] = user_service
        self.__cloudinary_service: Final[CloudinaryServiceABC] = cloudinary_service
        self.__editor_queries: Final[EditorQueriesABC] = editor_queries
        self.__converter_queries: Final[ConverterQueriesABC] = converter_queries
        self.__logger: Final[WebPEditorLoggerABC] = logger
        self.__user_id_key: Final[str] = "USER_ID"

    async def synchronize_async(self) -> None:
        """
        Updates the session store of current User.

        If the session has expired, it deletes the original and edited images, converted images, and the session store.
        """

        await self.__set_signed_user_id_async()

        current_expiry_age_minutes: int = await self.__get_expiry_age_minutes_async()

        user_id_result = await self.get_user_id_async()
        if user_id_result.is_error():
            self.__logger.log_error(
                f"Failed to get User ID. Reason: {user_id_result.error.message}. Error code: {user_id_result.error.error_code}"
            )
            return

        session_expiry_date = self.__request.session.get_expiry_date().astimezone(timezone.get_default_timezone())
        if timezone.now() > session_expiry_date:
            await user_id_result.map_async(self.__cleanup_storages_async)

        await self.set_expiry_async(timedelta(minutes=15))

        new_expiry_age_minutes: int = await self.__get_expiry_age_minutes_async()

        # Log messages
        self.__logger.log_debug(
            f"Current session expiration time of user '{user_id_result.ok}': {current_expiry_age_minutes} minute(s)"
        )
        self.__logger.log_debug(
            f"Updated session expiration time of user '{user_id_result.ok}': {new_expiry_age_minutes} minute(s)"
        )

    async def get_user_id_async(self) -> ContextResult[str]:
        return (await self.__get_signed_user_id_async()).bind(self.__user_service.unsign_id)

    async def set_expiry_async(self, duration: timedelta) -> None:
        await self.__request.session.aset_expiry(timezone.now() + duration)

    async def clear_expired_async(self) -> ContextResult[None]:
        user_id_result = await self.get_user_id_async()
        if user_id_result.is_error():
            return ContextResult[None].Error(user_id_result.error)

        await self.__request.session.aclear_expired()
        self.__logger.log_info(f"Expired session of User '{user_id_result.ok}' has been cleared")
        return ContextResult[None].Ok(None)

    async def __set_signed_user_id_async(self) -> None:
        # Create a new session
        if self.__get_session_key().is_none() or self.__request.session.is_empty():
            await self.__request.session.acreate()

        # Do nothing if the session contains a signed user id
        if (await self.__get_signed_user_id_async()).is_ok():
            return

        # Create an App User and get signed User ID
        signed_user_id = await self.__create_user_and_sign_id_async()

        # Set signed User ID to the session
        await self.__request.session.aset(self.__user_id_key, signed_user_id)

        self.__logger.log_debug(f"Signed User ID '{signed_user_id}' has been added into session storage")

    async def __get_expiry_age_minutes_async(self) -> int:
        return math.ceil(await self.__request.session.aget_expiry_age() / 60)

    async def __cleanup_storages_async(self, user_id: str) -> None:
        original_asset_result = await self.__editor_queries.get_original_asset_async(user_id)
        await original_asset_result.map_async(lambda original_asset: original_asset.adelete())

        edited_asset_result = await self.__editor_queries.get_edited_asset_async(user_id)
        await edited_asset_result.map_async(lambda edited_asset: edited_asset.adelete())

        converted_asset_result = await self.__converter_queries.get_converted_asset_async(user_id)
        await converted_asset_result.map_async(lambda converted_asset: converted_asset.adelete())

        self.__cloudinary_service.delete_original_and_edited_images(user_id)
        self.__cloudinary_service.delete_converted_images(user_id)

        (await self.clear_expired_async()).map_error(lambda error: self.__logger.log_error(error.message))

        self.__logger.log_debug("Storages have been cleaned up")

    async def __get_signed_user_id_async(self) -> ContextResult[str]:
        signed_user_id = await self.__request.session.aget(self.__user_id_key)

        if signed_user_id is None:
            return ContextResult[str].Error2(
                error_code=ErrorContext.ErrorCode.NOT_FOUND,
                message=f"Unable to find signed User ID under key {self.__user_id_key}",
            )

        return ContextResult[str].Ok(signed_user_id)

    async def __create_user_and_sign_id_async(self) -> str:
        key = self.__get_session_key().some
        expiration_date = self.__request.session.get_expiry_date()
        user: AppUser = await AppUser.objects.acreate(session_key=key, session_key_expiration_date=expiration_date)
        return self.__user_service.sign_id(str(user.id))

    def __get_session_key(self) -> Option[str]:
        return Option[str].of_optional(self.__request.session.session_key)
