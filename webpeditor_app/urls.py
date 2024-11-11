from django.conf.urls.static import static
from django.urls import path, URLResolver, URLPattern
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularAPIView

from webpeditor import settings
from webpeditor_app.api_views.converted_images_api_view import ConvertedImageCreateAPIView, ConvertedImageDeleteAPIView
from webpeditor_app.views.contact_view import contact_view
from webpeditor_app.views.about_view import about_view

from webpeditor_app.views.image_does_not_exist_view import image_does_not_exist_view
from webpeditor_app.views.image_edit_view import image_edit_view
from webpeditor_app.views.image_convert_view import image_convert_view
from webpeditor_app.views.image_info_view import image_info_view
from webpeditor_app.views.image_upload_view import image_upload_view
from webpeditor_app.views.unauthorized_access_view import unauthorized_access_view


# Templates
urlpatterns: list[URLResolver | URLPattern] = [
    path("", image_upload_view, name="ImageUploadView"),
    path("image_info/", image_info_view, name="ImageInfoView"),
    path("image_does_not_exist/", image_does_not_exist_view, name="ImageDoesNotExistView"),
    path("unauthorized_access/", unauthorized_access_view, name="UnauthorizedAccessView"),
    path("image_edit/", image_edit_view, name="ImageEditView"),
    path("image_convert/", image_convert_view, name="ImageConvertView"),
    path("about/", about_view, name="AboutView"),
    path("contact/", contact_view, name="ContactView"),
]

# API
urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/converter/converted-image-assets", ConvertedImageCreateAPIView.as_view(), name="converted-image-assets"),
    path("api/converter/converted-image-assets/<int:pk>", ConvertedImageDeleteAPIView.as_view(), name="converted-image-assets-delete"),
]

# urlpatterns += [
#     # For all non-existing (not allowed) urls
#     re_path(r"^.+$", no_content_view, name="NoContentView"),
# ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
