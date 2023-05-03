from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path

from webpeditor_app.views.image_does_not_exist_view import image_does_not_exist_view
from webpeditor_app.api.image_convert_api import image_convert_api
from webpeditor_app.api.image_download_api import image_download_api
from webpeditor_app.views.image_edit_view import image_edit_view
from webpeditor_app.views.image_convert_view import image_convert_view
from webpeditor_app.api.image_get_original_api import image_get_original_api
from webpeditor_app.views.image_info_view import image_info_view
from webpeditor_app.api.image_save_api import image_save_api
from webpeditor_app.views.image_upload_view import image_upload_view
from webpeditor_app.views.no_content_view import no_content_view

urlpatterns = [
    re_path(r'^$', image_upload_view, name='ImageUploadView'),
    re_path(r'^image_info/?$', image_info_view, name='ImageInfoView'),
    re_path(r'^image_does_not_exist/?$', image_does_not_exist_view, name='ImageDoesNotExistView'),
    re_path(r'^image_edit/?$', image_edit_view, name='ImageEditView'),
    re_path(r'^api/image_download/?$', image_download_api, name='ImageDownloadApi'),
    re_path(r'^api/image_save/?$', image_save_api, name='ImageSaveApi'),
    re_path(r'^api/image_get_original/?$', image_get_original_api, name='ImageGetOriginalApi'),
    re_path(r'^image_convert/?$', image_convert_view, name='ImageConvertView'),
    re_path(r'^api/image_convert/?$', image_convert_api, name='ImageConvertApi'),

    # For all non-existing (not allowed) urls
    re_path(r'^.+$', no_content_view, name='NoContentView'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
