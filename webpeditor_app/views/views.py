from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render

from webpeditor_app.services.session_id_to_db import set_session_expiry, update_session


def index(request: WSGIRequest):
    set_session_expiry(request)

    # TODO: get image id from DB
    # update_session(request, _id=...)
    return render(request, 'index.html')
