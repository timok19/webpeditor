from django.urls import re_path

from webpeditor_app.views.views import index
from webpeditor_app.controllers.image_requests.image_api_requests import original_image_api

urlpatterns = [
    re_path(r'^$', index, name='index'),
    re_path(r'^original_image/?$', original_image_api),
    re_path(r'^original_image/([0-9]+)$', original_image_api)
]
