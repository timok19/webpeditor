from typing import Union

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

from webpeditor_app.views.content_not_found_view import ContentNotFoundView

urlpatterns: list[Union[URLResolver, URLPattern]] = [
    # Admin
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    # TODO: Make dynamic URL Admin page access based on OTP code -> check out the perplexity chat
    path("admin/", admin.site.urls),
    # Account reset
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
    # WebP Editor
    path("", include("webpeditor_app.urls")),
    # For all non-existing (not allowed) urls
    re_path(r"^.+$", ContentNotFoundView.as_view(), name="content-not-found-view"),
]
