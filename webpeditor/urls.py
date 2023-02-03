from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from webpeditor.views import service_worker

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', service_worker),
    path('', include('webpeditor_app.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
