from typing import Union

from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import URLPattern, URLResolver, include, path, re_path
from django.views.generic import TemplateView

from views.about_view import AboutView
from views.contact_view import ContactView
from views.content_not_found_view import ContentNotFoundView
from views.image_converter_view import ImageConverterView
from views.image_not_found_view import ImageNotFoundView
from webpeditor import settings

# Admin
urlpatterns: list[Union[URLResolver, URLPattern]] = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    # TODO: Make dynamic URL Admin page access based on OTP code -> check out the perplexity chat
    path("admin/", admin.site.urls),
]

# Account reset
urlpatterns += [
    path(
        "accounts/password_reset/",
        PasswordResetView.as_view(extra_context={"site_header": admin.site.site_header}),
        name="admin_password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        PasswordResetDoneView.as_view(extra_context={"site_header": admin.site.site_header}),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(extra_context={"site_header": admin.site.site_header}),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        PasswordResetCompleteView.as_view(extra_context={"site_header": admin.site.site_header}),
        name="password_reset_complete",
    ),
    path("accounts/login/", LoginView.as_view(extra_context={"site_header": admin.site.site_header}), name="login"),
    path(
        "accounts/profile/",
        TemplateView.as_view(template_name="registration/profile.html", extra_context={"site_header": admin.site.site_header}),
        name="profile",
    ),
]

# Static files
if settings.IS_DEVELOPMENT:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# WebP Editor App
urlpatterns += [
    path("api/", include("api.urls")),
    path("image-not-found/", ImageNotFoundView.as_view(), name="image-not-found-view"),
    path("about/", AboutView.as_view(), name="about-view"),
    path("contact/", ContactView.as_view(), name="contact-view"),
    # path("", image_upload_view, name="image-uploader-view"),
    # path("info/", image_info_view, name="image-info-view"),
    # path("editor/", image_edit_view, name="image-editor-view"),
    path("converter/", ImageConverterView.as_view(), name="image-converter-view"),
    re_path(r"^.+$", ContentNotFoundView.as_view(), name="content-not-found-view"),
]
