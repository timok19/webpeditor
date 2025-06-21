from typing import Union

from django.conf.urls.static import static  # pyright: ignore [reportUnknownVariableType]
from django.urls import path, URLResolver, URLPattern, include

from webpeditor import settings
from webpeditor_app.api import webpeditor_api
from webpeditor_app.views.about_view import AboutView
from webpeditor_app.views.contact_view import ContactView
from webpeditor_app.views.image_not_found_view import ImageNotFoundView

# Templates
urlpatterns: list[Union[URLResolver, URLPattern]] = [
    path("api/", webpeditor_api.urls),
    path("image-not-found/", ImageNotFoundView.as_view(), name="image-not-found-view"),
    path("about/", AboutView.as_view(), name="about-view"),
    path("contact/", ContactView.as_view(), name="contact-view"),
    # path("", image_upload_view, name="image-uploader-view"),
    # path("image-info/", image_info_view, name="image-info-view"),
    # path("image-editor/", image_edit_view, name="image-editor-view"),
    # path("image-converter/", image_convert_view, name="image-converter-view"),
]

if settings.IS_DEVELOPMENT:
    # Static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Django Silk
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
