from typing import Union

from django.urls import URLResolver, URLPattern, path

from views.image_converter_view import ImageConverterView

urlpatterns: list[Union[URLResolver, URLPattern]] = [
    path("", ImageConverterView.as_view(), name="image-converter-view"),
    # path("", image_upload_view, name="image-uploader-view"),
    # path("image-info/", image_info_view, name="image-info-view"),
    # path("image-editor/", image_edit_view, name="image-editor-view"),
]
