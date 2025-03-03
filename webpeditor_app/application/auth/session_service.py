from datetime import timedelta
from typing import Final, Optional, final

from django.http.request import HttpRequest
from django.utils import timezone
from returns.maybe import Maybe, Nothing, Some

from webpeditor_app.core.extensions.result_extensions import (
    FailureContext,
    ResultExtensions,
    FutureContextResult,
)
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

        user_id_result = await self.get_user_id_async()

        if not await ResultExtensions.is_future_successful(user_id_result):
            (await user_id_result.awaitable()).alt(
                lambda failure: self.__logger.log_error(
                    f"Failed to get User ID. Reason: {failure.message}. Error code: {failure.error_code}"
                )
            )
            return None

        if timezone.now() > self.__request.session.get_expiry_date().astimezone(timezone.get_default_timezone()):
            await user_id_result.bind_awaitable(self.__cleanup_storages_async).awaitable()

        await self.set_expiry_async(timedelta(minutes=15))

        new_expiry_age_minutes: int = await self.__get_expiry_age_minutes_async()

        # Log messages
        user_id_io = (await user_id_result.awaitable()).unwrap()
        user_id_io.map(
            lambda user_id: self.__logger.log_debug(
                f"Current session expiration time of user '{user_id}': {current_expiry_age_minutes} minute(s)"
            )
        )
        user_id_io.map(
            lambda user_id: self.__logger.log_debug(
                f"Updated session expiration time of user '{user_id}': {new_expiry_age_minutes} minute(s)"
            )
        )

        return None

    async def get_user_id_async(self) -> FutureContextResult[str]:
        return (await self.__get_signed_user_id_async()).bind_result(self.__user_service.unsign_id)

    async def set_expiry_async(self, duration: timedelta) -> None:
        return await self.__request.session.aset_expiry(timezone.now() + duration)

    async def clear_expired_async(self) -> FutureContextResult[None]:
        return (await self.get_user_id_async()).bind_awaitable(self.__clear_expired_async)

    async def __clear_expired_async(self, user_id: str) -> None:
        await self.__request.session.aclear_expired()
        self.__logger.log_info(f"Expired session of User '{user_id}' has been cleared")
        return None

    async def __add_signed_user_id_async(self) -> None:
        if self.__request.session.is_empty():
            await self.__request.session.acreate()

        if await ResultExtensions.is_future_successful(await self.__get_signed_user_id_async()):
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
        await (
            (await self.__editor_queries.get_original_asset_async(user_id))
            .bind_awaitable(lambda original_asset: original_asset.adelete())
            .awaitable()
        )
        await (
            (await self.__editor_queries.get_edited_asset_async(user_id))
            .bind_awaitable(lambda edited_asset: edited_asset.adelete())
            .awaitable()
        )
        await (
            (await self.__converter_queries.get_converted_asset_async(user_id))
            .bind_awaitable(lambda converted_asset: converted_asset.adelete())
            .awaitable()
        )

        self.__cloudinary_service.delete_original_and_edited_images(user_id)
        self.__cloudinary_service.delete_converted_images(user_id)

        await (
            (await self.clear_expired_async())
            .alt(lambda failure: self.__logger.log_error(str(failure.message)))
            .awaitable()
        )

        self.__logger.log_debug("Storages have been cleaned up")

        return None

    async def __get_expiry_age_minutes_async(self) -> int:
        return round(await self.__request.session.aget_expiry_age() / 60)

    def __get_session_key(self) -> Maybe[str]:
        session_key: Optional[str] = self.__request.session.session_key
        return Some(session_key) if session_key is not None else Nothing

    async def __get_signed_user_id_async(self) -> FutureContextResult[str]:
        user_id: Optional[str] = await self.__request.session.aget(self.__user_id_key)
        return (
            ResultExtensions.future_failure(
                FailureContext.ErrorCode.INTERNAL_SERVER_ERROR,
                "Unable to get user ID from session storage",
            )
            if user_id is None
            else ResultExtensions.future_success(user_id)
        )
