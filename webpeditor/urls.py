from django.urls import path, include

from webpeditor.views import service_worker

urlpatterns = [
    path("sw.js", service_worker),
    path("", include("webpeditor_app.urls")),
]
