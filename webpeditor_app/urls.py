from django.urls import re_path
from django.conf.urls.static import static
from django.conf import settings

from webpeditor_app.views.views import index

from webpeditor_app.services.image_services.image_api_requests import original_image_api, edited_image_api, \
    upload_original_image, upload_edited_image

urlpatterns = [
    re_path(r'^$', index, name='index'),

    re_path(r'^original_image/?$', original_image_api),
    re_path(r'^original_image/([0-9]+)$', original_image_api),

    re_path(r'^edited_image/?$', edited_image_api),
    re_path(r'^edited_image/([0-9]+)$', edited_image_api),

    re_path(r'^original_image/upload/?$', upload_original_image),
    re_path(r'^edited_image/upload/?$', upload_edited_image)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
