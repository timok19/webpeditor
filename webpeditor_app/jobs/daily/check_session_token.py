import os
from pathlib import Path

from django.utils import timezone
from django_extensions.management.jobs import DailyJob

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.image_in_db_and_local import delete_old_image_in_db_and_local, \
    get_serialized_data_original_image
from webpeditor_app.services.image_services.user_folder import delete_expire_users_folder

import json


class Job(DailyJob):
    help = "Checks the estimated time of the session ID token and delete expired session, image from db and local"

    def execute(self):
        deserialized_data_from_db = get_serialized_data_original_image()
        try:
            original_images = OriginalImage.objects.all()
        except OriginalImage.DoesNotExist as error:
            raise error

        media_root: Path = settings.MEDIA_ROOT

        print(f"\n--- JSON object(s) in db ---\n{json.dumps(deserialized_data_from_db, indent=4)}")

        counter = 0
        if len(original_images) > 0:
            for image in original_images:
                user_id = image.user_id
                session_id_expiration_date = image.session_id_expiration_date

                if user_id and (timezone.now() > session_id_expiration_date):
                    delete_old_image_in_db_and_local(user_id)
                    counter += 1

                if not user_id:
                    delete_expire_users_folder(media_root)

                if user_id and not(user_id in os.listdir(media_root)):
                    delete_old_image_in_db_and_local(user_id)

            print(f"Deleted collections in db: {counter}")

        elif len(deserialized_data_from_db) == 0:
            delete_expire_users_folder(media_root)
