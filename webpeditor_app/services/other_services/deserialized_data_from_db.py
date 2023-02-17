from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.models.database.serializers import OriginalImageSerializer


def get_deserialized_data_from_db():
    try:
        original_images = OriginalImage.objects.all()
    except OriginalImage.DoesNotExist as error:
        raise error

    original_image_serializer = OriginalImageSerializer(original_images, many=True)

    return original_image_serializer.data
