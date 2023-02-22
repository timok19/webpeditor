from pathlib import Path

from django.contrib.sessions.models import Session
from django_extensions.management.jobs import DailyJob

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.image_in_db_and_local import delete_old_image_in_db_and_local
from webpeditor_app.services.image_services.session_update import update_session
from webpeditor_app.services.image_services.user_folder import delete_expire_users_folder
from webpeditor_app.services.other_services.deserialized_data_from_db import get_deserialized_data_from_db

import json


class Job(DailyJob):
    help = "Checks the estimated time of the session ID token and delete expired session, image from db and local"

    def execute(self):
        deserialized_data = get_deserialized_data_from_db()
        user_id: str
        session_id = str()
        media_root: Path = settings.MEDIA_ROOT
        user_id_to_delete = list()

        try:
            session_store = Session.objects.all()
        except Session.DoesNotExist as error:
            raise error

        print(f"\n--- JSON object in db ---\n{json.dumps(deserialized_data, indent=4)}")

        if len(deserialized_data) > 0:
            for data in deserialized_data:
                user_id = str(data["user_id"])

                session_store_decoded = [session.get_decoded() for session in session_store]
                try:
                    user_id_to_delete = [user_id_in_session_store["user_id"] for user_id_in_session_store in
                                         session_store_decoded]
                except KeyError as e:
                    print(f"{e} -> in session store does not exist")

                if user_id and (len(user_id_to_delete) == 0 or user_id_to_delete[0] is None):
                    delete_old_image_in_db_and_local(user_id)

                if len(session_store) > 0:
                    for session in session_store:
                        if user_id is None and user_id_to_delete[0]:
                            session.delete()

                        session_id = str(session.session_key)

                    update_session(session_id, user_id)

        # In case of session store is empty or if database data list is empty
        if len(session_store) == 0:
            OriginalImage.objects.all().delete()
            delete_expire_users_folder(media_root)
        elif len(deserialized_data) == 0:
            delete_expire_users_folder(media_root)
            session_store.delete()
