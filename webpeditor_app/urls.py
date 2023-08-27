from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path

from webpeditor_app.api.image_delete_converted_api import image_delete_converted_api
from webpeditor_app.api.image_download_converted_api import (
    image_download_converted_api,
    download_all_converted_api,
)
from webpeditor_app.views.contact_view import contact_view
from webpeditor_app.views.about_view import about_view

from webpeditor_app.views.image_does_not_exist_view import image_does_not_exist_view
from webpeditor_app.api.image_convert_api import image_convert_api
from webpeditor_app.api.image_download_edited_api import image_download_edited_api
from webpeditor_app.views.image_edit_view import image_edit_view
from webpeditor_app.views.image_convert_view import image_convert_view
from webpeditor_app.api.image_get_original_api import image_get_original_api
from webpeditor_app.views.image_info_view import image_info_view
from webpeditor_app.api.image_save_api import image_save_api
from webpeditor_app.views.image_upload_view import ImageUploadView
from webpeditor_app.views.no_content_view import NoContentView
from webpeditor_app.views.unauthorized_access_view import UnauthorizedAccessView


# Templates
urlpatterns = [
    re_path(r"^$", ImageUploadView.as_view(), name="ImageUploadView"),
    re_path(r"^image_info/?$", image_info_view, name="ImageInfoView"),
    re_path(
        r"^image_does_not_exist/?$",
        image_does_not_exist_view,
        name="ImageDoesNotExistView",
    ),
    re_path(
        r"^unauthorized_access/?$",
        UnauthorizedAccessView.as_view(),
        name="UnauthorizedAccessView",
    ),
    re_path(r"^image_edit/?$", image_edit_view, name="ImageEditView"),
    re_path(r"^image_convert/?$", image_convert_view, name="ImageConvertView"),
    re_path(r"^about/?$", about_view, name="AboutView"),
    re_path(r"^contact/?$", contact_view, name="ContactView"),
    # For all non-existing (not allowed) urls
    re_path(r"^.+$", NoContentView.as_view(), name="NoContentView"),
]

# APIs
urlpatterns += [
    re_path(
        r"^api/image_download_edited/?$",
        image_download_edited_api,
        name="ImageDownloadEditedApi",
    ),
    re_path(r"^api/image_save/?$", image_save_api, name="ImageSaveApi"),
    re_path(
        r"^api/image_get_original/?$",
        image_get_original_api,
        name="ImageGetOriginalApi",
    ),
    re_path(r"^api/image_convert/?$", image_convert_api, name="ImageConvertApi"),
    re_path(
        r"^api/image_download_converted/?$",
        image_download_converted_api,
        name="ImageDownloadConvertedApi",
    ),
    re_path(
        r"^api/download_all_converted/?$",
        download_all_converted_api,
        name="DownloadAllConvertedApi",
    ),
    re_path(
        r"^api/image_delete_converted/?$",
        image_delete_converted_api,
        name="ImageDeleteConvertedApi",
    ),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
