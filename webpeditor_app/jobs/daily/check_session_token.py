import json
import logging
from datetime import datetime

from django.utils import timezone
from django_extensions.management.jobs import DailyJob

from webpeditor_app.services.api_services.cloudinary_service import delete_all_folders, get_all_user_folders
from webpeditor_app.services.image_services.image_service import \
    delete_old_original_and_edited_image, \
    get_serialized_data_original_image, \
    get_serialized_data_edited_image, \
    get_all_original_images, \
    get_all_edited_images, delete_original_image_in_db, delete_edited_image_in_db
from webpeditor_app.services.other_services.session_service import clear_expired_session_store

logging.basicConfig(level=logging.INFO)


class Job(DailyJob):
    help = "Checks the estimated time of the session key and " \
           "delete expired session, images from db and images in Cloudinary storage"

    def execute(self):
        original_images_deserialized = get_serialized_data_original_image()
        edited_images_deserialized = get_serialized_data_edited_image()

        original_images = get_all_original_images()
        edited_images = get_all_edited_images()
        user_folders: list = get_all_user_folders()

        logging.info(
            f"\n--- Original Image object(s) in db ---"
            f"\n{json.dumps(original_images_deserialized, indent=4)}"
        )
        logging.info(
            f"\n--- Edited Image object(s) in db ---"
            f"\n{json.dumps(edited_images_deserialized, indent=4)}"
        )

        counter = 0

        if len(original_images) == 0 or len(edited_images) == 0:
            delete_all_folders()

        if len(original_images) > 0:
            for image in original_images:
                user_id: str = image.user_id
                session_key: str = image.session_key
                session_key_expiration_date: datetime = image.session_key_expiration_date

                if (timezone.now() > session_key_expiration_date) and (user_id in user_folders):
                    logging.info("Session is expired. Deleting original image, edited image and session store...")
                    delete_old_original_and_edited_image(user_id)
                    clear_expired_session_store(session_key)
                    counter += 1
                elif user_id not in user_folders:
                    delete_original_image_in_db(user_id)
                    delete_edited_image_in_db(user_id)
                    counter += 1

        logging.info(f"Deleted collections in db: {counter}")
