from django.contrib.auth.views import PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView
from django.urls import path, include

from webpeditor_app.admin import admin_site

urlpatterns = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin_site.urls),
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
    path("", include("webpeditor_app.urls")),
]
