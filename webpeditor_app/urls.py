from django.urls import path

from webpeditor_app.views.views import index

urlpatterns = [
    path('', index, name='index'),
]
