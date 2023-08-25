import logging
from uuid import UUID, uuid4

from beanie.odm.operators.update.general import Set
from django.contrib.sessions.backends.db import SessionStore
from django.core.handlers.asgi import ASGIRequest
from django.core import signing
from django.http import JsonResponse

from datetime import datetime, timedelta

from webpeditor_app.services.external_api_services.cloudinary_service import (
    CloudinaryService,
)
from webpeditor_app.commands.original_images_commands import OriginalImagesCommands
from webpeditor_app.commands.edited_images_commands import EditedImagesCommands


class SessionService:
    logging.basicConfig(level=logging.INFO)

    user_id: UUID | None = None

    def __init__(self, request: ASGIRequest):
        self.request = request
        self.session_store = SessionStore(session_key=self.request.session.session_key)

    def set_session_expiry(self, number_of_seconds: int):
        self.request.session.set_expiry(number_of_seconds)

    def add_signed_user_id_to_session_store(self):
        self.request.session["user_id"] = signing.dumps(uuid4())

    def get_unsigned_user_id(self):
        try:
            signed_user_id = self.request.session.get("user_id")
            if signed_user_id is not None:
                self.user_id = signing.loads(signed_user_id)
        except Exception as e:
            logging.error(e)

    def update_session_store(self):
        self.session_store.encode(
            session_dict={
                "user_id": self.request.session.get("user_id"),
            }
        )

        update_expiration = datetime.utcnow() + timedelta(seconds=900)

        self.session_store.set_expiry(value=update_expiration)

    def clear_expired_session_store(self):
        self.session_store.clear_expired()
        logging.info("Session has been cleared")

    def log_session_expiration_times(
        self,
        current_time_expiration_minutes: int,
        new_time_expiration_minutes: int,
    ):
        logging.info(
            f"Current session expiration time of user '{self.user_id}': "
            f"{current_time_expiration_minutes} minute(s)"
        )

        logging.info(
            f"Updated session expiration time of user '{self.user_id}': "
            f"{new_time_expiration_minutes} minute(s)"
        )

    async def update_session_expiration_date_in_db(self):
        original_image = await OriginalImagesCommands.get_original_image(self.user_id)
        if original_image is None:
            return JsonResponse(
                data={
                    "success": False,
                    "error": "Original image was not found",
                },
                status=404,
            )

        edited_image = await EditedImagesCommands.get_edited_image(self.user_id)
        if edited_image is None:
            return JsonResponse(
                data={
                    "success": False,
                    "error": "Edited image was not found",
                },
                status=404,
            )

        expiry_date = self.session_store.get_expiry_date()
        original_image.update(
            Set({original_image.item.session_key_expiration_date: expiry_date})
        )
        edited_image.update(
            Set({edited_image.item.session_key_expiration_date: expiry_date})
        )

        return

    async def update_session(self):
        current_time_expiration_minutes = round(
            self.session_store.get_expiry_age() / 60
        )

        expiry_date = self.session_store.get_expiry_date()
        now = datetime.utcnow()

        if now > expiry_date:
            await OriginalImagesCommands.delete_original_image(self.user_id)
            CloudinaryService.delete_original_and_edited_images(self.user_id.__str__())
            CloudinaryService.delete_converted_images(self.user_id.__str__())
            self.clear_expired_session_store()

        self.update_session_store()

        new_time_expiration_minutes = round(self.session_store.get_expiry_age() / 60)

        self.log_session_expiration_times(
            current_time_expiration_minutes,
            new_time_expiration_minutes,
        )

        await self.update_session_expiration_date_in_db()

        return JsonResponse(
            data={
                "success": True,
                "info": "Session is alive",
                "estimated_time_of_session_id": current_time_expiration_minutes,
            },
            status=200,
        )
