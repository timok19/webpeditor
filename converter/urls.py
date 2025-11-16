from typing import Union

from django.urls import URLResolver, URLPattern, path

from views.image_converter_view import ImageConverterView

urlpatterns: list[Union[URLResolver, URLPattern]] = [path("", ImageConverterView.as_view(), name="image-converter-view")]
