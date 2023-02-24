from pathlib import Path

from django.utils import timezone
from django_extensions.management.jobs import DailyJob

from webpeditor import settings
from webpeditor_app.services.image_services.image_in_db_and_local import delete_old_image_in_db_and_local
from webpeditor_app.services.image_services.user_folder import delete_expire_users_folder
from webpeditor_app.services.other_services.deserialized_data_from_db import get_deserialized_data_from_db

import json


class Job(DailyJob):
    help = "Checks the estimated time of the session ID token and delete expired session, image from db and local"

    def execute(self):
        deserialized_data = get_deserialized_data_from_db()
        user_id: str
        media_root: Path = settings.MEDIA_ROOT

        print(f"\n--- JSON object(s) in db ---\n{json.dumps(deserialized_data, indent=4)}")

        counter = 0
        if len(deserialized_data) > 0:
            for data in deserialized_data:
                user_id = str(data["user_id"])
                session_id_expiration_date = data["session_id_expiration_date"]

                if user_id and timezone.now() > session_id_expiration_date:
                    delete_old_image_in_db_and_local(user_id)
                    counter += 1

                print(f"Deleted collections in db: {counter}")

        elif len(deserialized_data) == 0:
            delete_expire_users_folder(media_root)
