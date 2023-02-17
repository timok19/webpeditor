from django.contrib.sessions.models import Session
from django_extensions.management.jobs import DailyJob
from webpeditor_app.services.image_services.session_id_to_db import update_session
from webpeditor_app.services.other_services.deserialized_data_from_db import get_deserialized_data_from_db

import json


class Job(DailyJob):
    help = "Checks the estimated time of the session ID token and delete expired session, image from db and local"

    user_id: str
    session_id: str

    def execute(self):
        deserialized_data = get_deserialized_data_from_db()
        try:
            session_store = Session.objects.all()
        except Session.DoesNotExist as error:
            raise error

        print(f"JSON object in db:\n{json.dumps(deserialized_data, indent=4)}")

        for data in deserialized_data:
            self.user_id = str(data["user_id"])
            for session in session_store:
                self.session_id = session.session_key
            update_session(self.session_id, self.user_id)
