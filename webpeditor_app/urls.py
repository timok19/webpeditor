from django.urls import re_path
from django.conf.urls.static import static
from django.conf import settings

from webpeditor_app.views.views import upload_image_view, show_image_info_view, image_does_not_exist_view
from webpeditor_app.services.image_services.image_api_requests \
    import \
    original_image_api, \
    edited_image_api, \
    upload_edited_image

urlpatterns = [
    re_path(r'^$', upload_image_view, name='UploadImageView'),
    re_path(r'^image_info/?$', show_image_info_view, name='ImageInfoView'),
    re_path(r'^image_does_not_exit/$', image_does_not_exist_view, name='ImageDoesNotExistView'),

    re_path(r'^original_image/?$', original_image_api),
    re_path(r'^original_image/([0-9]+)$', original_image_api),

    re_path(r'^edited_image/?$', edited_image_api),
    re_path(r'^edited_image/([0-9]+)$', edited_image_api),

    re_path(r'^edited_image/upload/?$', upload_edited_image),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
