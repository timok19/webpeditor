from datetime import timedelta, datetime
from typing import Optional

from django.utils import timezone
from rest_framework.request import Request

from webpeditor_app.common.resultant import ResultantValue, Resultant, ErrorCode
from webpeditor_app.core.auth.user import UserServiceABC
from webpeditor_app.core.logging import LoggerABC
from webpeditor_app.infrastructure.cloudinary import CloudinaryServiceABC
from webpeditor_app.models import OriginalImageAsset, EditedImageAsset, ConvertedImageAsset


class SessionService:
    def __init__(
        self,
        request: Request,
        user_service: UserServiceABC,
        cloudinary_service: CloudinaryServiceABC,
        logger: LoggerABC,
    ) -> None:
        self.__request: Request = request
        self.__user_service: UserServiceABC = user_service
        self.__cloudinary_service: CloudinaryServiceABC = cloudinary_service
        self.__logger: LoggerABC = logger

    def set_session_expiry(self, duration: timedelta) -> None:
        self.__request.session.set_expiry(timezone.now() + duration)

    def add_or_get_signed_user_id(self) -> ResultantValue[str]:
        existing_signed_user_id_resultant: ResultantValue[str] = self.get_signed_user_id()

        if Resultant.is_successful(existing_signed_user_id_resultant):
            return existing_signed_user_id_resultant

        created_signed_user_id: str = self.__user_service.create_signed_user_id().unwrap()

        self.__request.session["user_id"] = created_signed_user_id

        return Resultant.success(created_signed_user_id)

    def get_signed_user_id(self) -> ResultantValue[str]:
        user_id: Optional[str] = self.__request.session.get("user_id")

        if user_id is None:
            return Resultant.error("User ID not found in session store", error_code=ErrorCode.NOT_FOUND)

        return Resultant.success(user_id)

    def clear_expired_session_store(self) -> None:
        self.__request.session.clear_expired()
        self.__logger.log_info("Expired session has been cleared")

    def update_session_store(self) -> ResultantValue[int]:
        """
        Updates the session store with the current user ID.
        If the session has expired, it deletes the original and edited images, converted images, and the session store.

        Returns the number of minutes remaining in the session.
        """

        signed_user_id_resultant: ResultantValue[str] = self.get_signed_user_id()

        if not Resultant.is_successful(signed_user_id_resultant):
            return Resultant.from_failure(signed_user_id_resultant.failure())

        session_store_expiry_minutes: int = self.__get_session_expiry_in_minutes()
        session_store_expiry_datetime: datetime = timezone.localtime(self.__request.session.get_expiry_date())
        datetime_now: datetime = timezone.localtime(timezone.now())

        signed_user_id: str = signed_user_id_resultant.unwrap()

        unsigned_user_id_resultant: ResultantValue[str] = self.__user_service.unsign_user_id(signed_user_id)

        if not Resultant.is_successful(unsigned_user_id_resultant):
            return Resultant.from_failure(unsigned_user_id_resultant.failure())

        unsigned_user_id: str = unsigned_user_id_resultant.unwrap()

        if datetime_now > session_store_expiry_datetime:
            # delete_original_image_in_db(user_id)
            self.__cloudinary_service.delete_original_and_edited_images(unsigned_user_id)
            self.__cloudinary_service.delete_converted_images(unsigned_user_id)
            self.clear_expired_session_store()

        self.set_session_expiry(timedelta(minutes=15))

        new_session_store_expiry_minutes: int = self.__get_session_expiry_in_minutes()

        self.__logger.log_info(f"Current session expiration time of user '{unsigned_user_id}': {session_store_expiry_minutes} minute(s)")
        self.__logger.log_info(f"Updated session expiration time of user '{unsigned_user_id}': {new_session_store_expiry_minutes} minute(s)")

        self.__update_image_assets_expirations(unsigned_user_id)

        return Resultant.success(session_store_expiry_minutes)

    def __get_session_expiry_in_minutes(self) -> int:
        return round(self.__request.session.get_expiry_age() / 60)

    def __update_image_assets_expirations(self, user_id: str) -> None:
        session_expiry_date: datetime = self.__request.session.get_expiry_date()

        original_image_asset: Optional[OriginalImageAsset] = OriginalImageAsset.objects.filter(user_id=user_id).first()

        if original_image_asset is not None:
            original_image_asset.objects.update(session_key_expiration_date=session_expiry_date)

        edited_image_asset: Optional[EditedImageAsset] = EditedImageAsset.objects.filter(user_id=user_id).first()

        if edited_image_asset is not None:
            edited_image_asset.objects.update(session_key_expiration_date=session_expiry_date)

        converted_image_asset: Optional[ConvertedImageAsset] = ConvertedImageAsset.objects.filter(user_id=user_id).first()

        if converted_image_asset is not None:
            converted_image_asset.objects.update(session_key_expiration_date=session_expiry_date)
