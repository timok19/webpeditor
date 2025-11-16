from typing import Union
from django.urls import URLResolver, URLPattern, path

from api import registration


urlpatterns: list[Union[URLResolver, URLPattern]] = [path("", registration.api.urls)]
