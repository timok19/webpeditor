from django.contrib import admin
from django.urls import path, include
from .views import service_worker

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', service_worker),
    path('', include('webpeditor_app.urls'))
]
