from django.views.decorators.csrf import csrf_exempt
from django_extensions.management.jobs import DailyJob
from webob import Request
from webpeditor_app.services.image_services.session_id_to_db import update_session
from webpeditor.settings import CORS_ORIGIN_WHITELIST

import json


class Job(DailyJob):
    help = "Checks the estimated time of the session ID token and delete expired session, image from db and local"

    request: Request = None
    session_id: str = None

    # Change from CORS_ORIGIN_WHITELIST to domain name
    base_url = CORS_ORIGIN_WHITELIST[0] or CORS_ORIGIN_WHITELIST[1]

    @csrf_exempt
    def execute(self):
        request = Request.blank(path='/original_image', base_url=self.base_url)
        request.method = 'GET'

        response = request.get_response()
        response_body: bytes = response.body
        status_code: int = response.status_code

        if status_code == 200:
            deserialized_data = json.loads(response_body)

            print(f"JSON object in db:\n{json.dumps(deserialized_data, indent=4)}")

            for data in deserialized_data:
                self.session_id = str(data["session_id"])
                update_session(self.session_id)
