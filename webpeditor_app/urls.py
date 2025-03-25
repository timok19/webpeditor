from typing import Union
from django.conf.urls.static import static
from django.urls import path, URLResolver, URLPattern, re_path, include

from webpeditor import settings
from webpeditor_app.api import webpeditor_api
from webpeditor_app.views.contact_view import ContactView
from webpeditor_app.views.about_view import AboutView

from webpeditor_app.views.image_not_found_view import ImageNotFoundView

from webpeditor_app.views.content_not_found_view import ContentNotFoundView


# Templates
urlpatterns: list[Union[URLResolver, URLPattern]] = [
    path("api/", webpeditor_api.urls, name="webpeditor-api"),
    # path("image-info/", image_info_view, name="image-info-view"),
    # path("image-editor/", image_edit_view, name="image-editor-view"),
    # path("image-converter/", image_convert_view, name="image-converter-view"),
    # path("", image_upload_view, name="image-uploader-view"),
    path("image-not-found/", ImageNotFoundView.as_view(), name="image-not-found-view"),
    path("about/", AboutView.as_view(), name="about-view"),
    path("contact/", ContactView.as_view(), name="contact-view"),
]

if settings.DEBUG:
    # Static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Django Silk
    urlpatterns.append(path("silk/", include("silk.urls", namespace="silk")))

# For all non-existing (not allowed) urls
urlpatterns.append(re_path(r"^.+$", ContentNotFoundView.as_view(), name="no-content-found-view"))
