from typing import Union

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import path, include, URLPattern, URLResolver, re_path

from webpeditor_app.admin import admin_site
from webpeditor_app.views.content_not_found_view import ContentNotFoundView

# Admin
urlpatterns: list[Union[URLResolver, URLPattern]] = [
    # TODO: Make dynamic URL Admin page access based on OTP code -> check out the perplexity chat
    path("admin/", admin_site.urls),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
]

# Account reset
urlpatterns += [
    path(
        "accounts/password_reset/",
        PasswordResetView.as_view(extra_context={"site_header": admin_site.site_header}),
        name="admin_password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        PasswordResetDoneView.as_view(extra_context={"site_header": admin_site.site_header}),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(extra_context={"site_header": admin_site.site_header}),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        PasswordResetCompleteView.as_view(extra_context={"site_header": admin_site.site_header}),
        name="password_reset_complete",
    ),
]

# QStash
urlpatterns += [path("qstash/webhook/", include("django_qstash.urls"))]

# WebP Editor
urlpatterns += [path("", include("webpeditor_app.urls"))]

# For all non-existing (not allowed) urls
urlpatterns += [re_path(r"^.+$", ContentNotFoundView.as_view(), name="content-not-found-view")]
