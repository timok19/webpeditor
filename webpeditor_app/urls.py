from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

from webpeditor_app.views.image_does_not_exist_view import image_does_not_exist_view
from webpeditor_app.views.image_edit_view import image_edit_view
from webpeditor_app.views.image_convert_view import image_convert_view
from webpeditor_app.views.image_info_view import image_info_view
from webpeditor_app.views.image_upload_view import image_upload_view
from webpeditor_app.views.no_content_view import no_content_view

urlpatterns = [
    re_path(r'^$', image_upload_view, name='ImageUploadView'),
    re_path(r'^image_info/?$', image_info_view, name='ImageInfoView'),
    re_path(r'^image_does_not_exist/?$', image_does_not_exist_view, name='ImageDoesNotExistView'),
    re_path(r'^image_edit/?$', image_edit_view, name='ImageEditView'),
    re_path(r'^image_convert/?$', image_convert_view, name='ImageConvertView'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # For all non-existing (not allowed) urls
    re_path(r'^.+$', no_content_view, name='NoContentView'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
