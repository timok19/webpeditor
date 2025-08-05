from typing import Union

from django.conf.urls.static import static
from django.urls import URLPattern, URLResolver, path
from ninja_extra import NinjaExtraAPI

from webpeditor import settings
from webpeditor_app.api.authentication.authenticator import APIKeyAuthenticator
from webpeditor_app.api.controllers.image_converter_controller import ImageConverterController
from webpeditor_app.views.about_view import AboutView
from webpeditor_app.views.contact_view import ContactView
from webpeditor_app.views.image_converter_view import ImageConverterView
from webpeditor_app.views.image_not_found_view import ImageNotFoundView


# API
api = NinjaExtraAPI(title=settings.APP_VERBOSE_NAME, version=settings.APP_VERSION, auth=APIKeyAuthenticator())
api.register_controllers(ImageConverterController)  # pyright: ignore

urlpatterns: list[Union[URLResolver, URLPattern]] = [
    # API
    path("api/", api.urls),
    # Templates
    path("image-not-found/", ImageNotFoundView.as_view(), name="image-not-found-view"),
    path("about/", AboutView.as_view(), name="about-view"),
    path("contact/", ContactView.as_view(), name="contact-view"),
    path("converter/", ImageConverterView.as_view(), name="image-converter-view"),
    # path("", image_upload_view, name="image-uploader-view"),
    # path("image-info/", image_info_view, name="image-info-view"),
    # path("image-editor/", image_edit_view, name="image-editor-view"),
]

# Static files
if settings.IS_DEVELOPMENT:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
