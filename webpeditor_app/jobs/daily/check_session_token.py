import os
import shutil
from datetime import datetime
from pathlib import Path

from django.utils import timezone
from django_extensions.management.jobs import DailyJob

from webpeditor import settings
from webpeditor_app.services.image_services.image_in_db_and_local import delete_old_image_in_db_and_local, \
    get_deserialized_data_from_db
from webpeditor_app.services.image_services.user_folder import delete_expire_users_folder

import json


class Job(DailyJob):
    help = "Checks the estimated time of the session ID token and delete expired session, image from db and local"

    def execute(self):
        deserialized_data_from_db = get_deserialized_data_from_db()
        user_id: str
        media_root: Path = settings.MEDIA_ROOT

        print(f"\n--- JSON object(s) in db ---\n{json.dumps(deserialized_data_from_db, indent=4)}")

        counter = 0
        if len(deserialized_data_from_db) > 0:
            for data in deserialized_data_from_db:
                user_id = str(data["user_id"])
                session_id_expiration_date = datetime.strptime(
                    data["session_id_expiration_date"],
                    "%Y-%m-%dT%H:%M:%S.%f%z"
                )

                if user_id and timezone.now() > session_id_expiration_date:
                    delete_old_image_in_db_and_local(user_id)
                    counter += 1

                uploaded_images_subfolders = next(os.walk(media_root))[1]
                if user_id not in uploaded_images_subfolders:
                    for folder in os.listdir(media_root):
                        if os.path.isdir(os.path.join(media_root, folder)) and folder != user_id:
                            print(f"Deleting folder: {folder}")
                            shutil.rmtree(os.path.join(media_root, folder))

            print(f"Deleted collections in db: {counter}")

        elif len(deserialized_data_from_db) == 0:
            delete_expire_users_folder(media_root)
