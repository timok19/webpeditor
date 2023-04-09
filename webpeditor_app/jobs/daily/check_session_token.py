import json
import logging
import os
from pathlib import Path

from django.utils import timezone
from django_extensions.management.jobs import DailyJob

from webpeditor import settings
from webpeditor_app.services.image_services.folder_service import delete_folder_by_expiry
from webpeditor_app.services.image_services.image_service import delete_old_image_in_db_and_local, \
    get_serialized_data_original_image, get_serialized_data_edited_image, get_all_original_images, get_all_edited_images

logging.basicConfig(level=logging.INFO)


class Job(DailyJob):
    help = "Checks the estimated time of the session ID token and delete expired session, image from db and local"

    def execute(self):
        original_images_deserialized = get_serialized_data_original_image()
        edited_images_deserialized = get_serialized_data_edited_image()

        media_root: Path = settings.MEDIA_ROOT

        logging.info(
            f"\n--- Original Image object(s) in db ---\n{json.dumps(original_images_deserialized, indent=4)}"
        )
        logging.info(
            f"\n--- Edited Image object(s) in db ---\n{json.dumps(edited_images_deserialized, indent=4)}"
        )

        counter = 0
        if len(original_images_deserialized) > 0:
            for image in original_images_deserialized:
                user_id = image["user_id"]
                session_id_expiration_date = image["session_id_expiration_date"]

                if timezone.now() > session_id_expiration_date:
                    delete_old_image_in_db_and_local(user_id)
                    counter += 1

                if user_id and not (user_id in os.listdir(media_root)):
                    delete_folder_by_expiry(media_root)

                if not user_id:
                    logging.error("There is no original images. Deleting users folders...")
                    delete_folder_by_expiry(media_root)

            logging.info(f"Deleted collections in db: {counter}")

        if len(edited_images) > 0:
            for image in edited_images:
                user_id = image.user_id
                if not user_id:
                    delete_folder_by_expiry(media_root)

                delete_old_image_in_db_and_local(user_id)

        if len(original_images_deserialized) == 0 or len(edited_images_deserialized) == 0:
            delete_folder_by_expiry(media_root)
