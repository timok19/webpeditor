from django.urls import re_path
from webpeditor_app.views.views import original_image_api

from webpeditor_app.views.views import index

urlpatterns = [
    re_path(r'^$', index, name='index'),
    re_path(r'^original_image/?$', original_image_api)
]
