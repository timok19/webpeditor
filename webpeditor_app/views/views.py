from django.core.handlers.wsgi import WSGIRequest
# from django.shortcuts import render, redirect

from webpeditor_app.services.image_services.image_api_requests import upload_original_image
from webpeditor_app.services.session_id_to_db import set_session_expiry


def index(request: WSGIRequest):
    set_session_expiry(request)
    # TODO: fix problem with tuple "return value tuple[] -> HttpResponsePermanentRedirect | HttpResponseRedirect"
    return upload_original_image(request)
