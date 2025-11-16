from typing import Union

from django.urls import URLResolver, URLPattern


urlpatterns: list[Union[URLResolver, URLPattern]] = [
    # path("", image_upload_view, name="image-uploader-view"),
    # path("image-info/", image_info_view, name="image-info-view"),
    # path("image-editor/", image_edit_view, name="image-editor-view"),
]
