from datetime import datetime, timedelta
from typing import Final, Optional, final

from django.http.request import HttpRequest
from django.utils import timezone
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import is_successful

from webpeditor_app.core.extensions.result_extensions import FailureContext, ContextResult, ResultExtensions
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.infrastructure.database.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.infrastructure.database.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.infrastructure.abc.cloudinary_service_abc import CloudinaryServiceABC
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
        self.__user_id_key: Final[str] = "user_id"

    async def synchronize_async(self) -> None:
        """
        Updates the session store of current User.

        If the session has expired, it deletes the original and edited images, converted images, and the session store.
        """

        await self.__add_signed_user_id_async()

        current_expiry_age_minutes: int = await self.__get_expiry_age_minutes_async()

        session_store_expiry_datetime: datetime = self.__request.session.get_expiry_date().astimezone(
            timezone.get_default_timezone()
        )
        datetime_now: datetime = timezone.now()

        user_id_result: ContextResult[str] = await self.get_user_id_async()

        if not is_successful(user_id_result):
            failure: FailureContext = user_id_result.failure()
            self.__logger.log_error(
                f"Failed to get User ID. Reason: {failure.message}. Error code: {failure.error_code}"
            )
            return

        user_id: str = user_id_result.unwrap()

        if datetime_now > session_store_expiry_datetime:
            await self.__cleanup_storages_async(user_id)

        await self.set_expiry_async(timedelta(minutes=15))

        new_expiry_age_minutes: int = await self.__get_expiry_age_minutes_async()

        self.__logger.log_debug(
            f"Current session expiration time of user '{user_id}': {current_expiry_age_minutes} minute(s)"
        )
        self.__logger.log_debug(
            f"Updated session expiration time of user '{user_id}': {new_expiry_age_minutes} minute(s)"
        )

        return None

    async def get_user_id_async(self) -> ContextResult[str]:
        return (await self.__get_signed_user_id_async()).bind(self.__user_service.unsign_id)

    async def set_expiry_async(self, duration: timedelta) -> None:
        return await self.__request.session.aset_expiry(timezone.now() + duration)

    async def clear_expired_async(self) -> ContextResult[None]:
        return (
            (await self.get_user_id_async())
            .map(lambda user_id: (user_id, self.__request.session.clear_expired()))
            .map(lambda result: self.__logger.log_info(f"Expired session of user '{result[0]}' has been cleared"))
        )

    async def __add_signed_user_id_async(self) -> None:
        if self.__request.session.is_empty():
            await self.__request.session.acreate()

        if is_successful(await self.__get_signed_user_id_async()):
            return None

        user: AppUser = await AppUser.objects.acreate(
            session_key=self.__get_session_key().unwrap(),
            session_key_expiration_date=self.__request.session.get_expiry_date(),
        )

        signed_id = self.__user_service.sign_id(user.id)
        await self.__request.session.aset(self.__user_id_key, signed_id)

        self.__logger.log_debug(f"Signed User ID '{signed_id}' has been added into session storage")

        return None

    async def __cleanup_storages_async(self, user_id: str) -> None:
        (await self.__editor_queries.get_original_asset_async(user_id)).map(lambda asset: asset.delete())
        (await self.__editor_queries.get_edited_asset_async(user_id)).map(lambda asset: asset.delete())
        (await self.__converter_queries.get_converted_asset_async(user_id)).map(lambda asset: asset.delete())

        self.__cloudinary_service.delete_original_and_edited_images(user_id)
        self.__cloudinary_service.delete_converted_images(user_id)

        (await self.clear_expired_async()).alt(
            lambda failure: self.__logger.log_error(failure.message or "Unable to clean expired session store")
        )

        self.__logger.log_debug("Storages have been cleaned up")

        return None

    async def __get_expiry_age_minutes_async(self) -> int:
        return round(await self.__request.session.aget_expiry_age() / 60)

    def __get_session_key(self) -> Maybe[str]:
        session_key: Optional[str] = self.__request.session.session_key
        return Some(session_key) if session_key is not None else Nothing

    async def __get_signed_user_id_async(self) -> ContextResult[str]:
        user_id: Optional[str] = await self.__request.session.aget(self.__user_id_key)
        if user_id is None:
            return ResultExtensions.failure(
                FailureContext.ErrorCode.INTERNAL_SERVER_ERROR,
                "Unable to get user ID from session storage",
            )

        return ResultExtensions.success(user_id)
