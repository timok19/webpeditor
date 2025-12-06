from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def image_info_view():
    ...
    # user_id: str | HttpResponse = get_user_id_or_401(request)
    # if isinstance(user_id, HttpResponse):
    #     return user_id
    #
    # original_image: EditorOriginalImageAsset | HttpResponse = get_original_image_or_401(request, user_id)
    # if isinstance(original_image, HttpResponse):
    #     return original_image
    #
    # image_data: BytesIO | None = get_data_from_image_url(original_image.image_url)
    # if isinstance(image_data, NoneType):
    #     return redirect("image-not-found-view")
    #
    # # Image info taken from file
    # image_info: tuple | None = get_image_info(image_data)
    # if isinstance(image_info, NoneType):
    #     return redirect("image-not-found-view")
    #
    # image_format_description: str = image_info[0]  # pyright: ignore [reportAssignmentType]
    # image_format: str = image_info[1]  # pyright: ignore [reportAssignmentType]
    # image_size: str = image_info[2]
    # image_resolution: str = image_info[3]
    # image_aspect_ratio: Decimal = image_info[4]
    # image_mode: str = image_info[5]
    #
    # context: dict = {
    #     "original_image_url": original_image.image_url,
    #     "image_name": cut_image_name(f"{original_image.image_name}.{image_format.lower()}", 20),
    #     "image_format": image_format_description,
    #     "image_size": image_size,
    #     "image_resolution": image_resolution,
    #     "aspect_ratio": image_aspect_ratio,
    #     "image_mode": image_mode,
    # }
    #
    # update_session(request=request, user_id=user_id)
    #
    # return render(request, "webpeditor_app/image-info.html", context, status=200)
