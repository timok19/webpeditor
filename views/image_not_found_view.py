from views.content_not_found_view import ContentNotFoundView


class ImageNotFoundView(ContentNotFoundView):
    extra_context = {"message": "Image not found"}
