from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage, DefaultStorage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.models.database.serializers import OriginalImageSerializer, EditedImageSerializer
from webpeditor_app.services.image_services.re_for_file_name import replace_with_underscore
from webpeditor_app.services.session_id_to_db import set_session_expiry
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


@csrf_exempt
def original_image_api(request: WSGIRequest, _id=0) -> JsonResponse:
    """Function implementation of API methods to store original_image into DB

    Parameters:
        request: WSGIRequest

            API request (GET, POST, DELETE)

        _id: int

            image_id to delete using DELETE API method

    Returns:
        json_response: JsonResponse()
    """

    if request.method == 'DELETE':
        try:
            original_image_id = OriginalImage.objects.get(image_id=_id)
        except OriginalImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'})

        original_image_id.delete()
        default_storage.delete(original_image_id.original_image_url.name)

        return JsonResponse("Deleted successfully", safe=False)


# TODO: implement this method to call http requests for edited image
@csrf_exempt
def edited_image_api(request: WSGIRequest, _id=0) -> JsonResponse:
    """Function implementation of API methods to store edited_image into DB

    Parameters:
        request: WSGIRequest

            API request (GET, POST, DELETE)

        _id: int

            image_id to delete using DELETE API method

    Returns:
        json_response: JsonResponse()
    """
    if request.method == 'GET':
        edited_images = EditedImage.objects.all()
        edited_image_serializer = EditedImageSerializer(edited_images, many=True)

        return JsonResponse(edited_image_serializer.data, safe=False)

    elif request.method == 'POST':
        edited_image_data = JSONParser().parse(request)
        edited_image_serializer = EditedImageSerializer(data=edited_image_data)

        if edited_image_serializer.is_valid():
            edited_image_serializer.save()

            return JsonResponse("Added edited image to db successfully", safe=False)

        return JsonResponse("Failed to add edited image into db", safe=False)

    elif request.method == 'PUT':
        edited_image_data = JSONParser().parse(request)
        edited_image = EditedImage.objects.get(image_id=edited_image_data['image_id'])
        edited_image_serializer = EditedImageSerializer(edited_image, data=edited_image_data)

        if edited_image_serializer.is_valid():
            edited_image_serializer.save()

            return JsonResponse("Updated edited image in db successfully", safe=False)

        return JsonResponse("Failed to update edited image in db", safe=False)

    elif request.method == 'DELETE':
        edited_image = EditedImage.objects.get(image_id=_id)
        edited_image.delete()

        return JsonResponse("Deleted edited image successfully", safe=False)


# TODO: implement this method to reupload edited image to project path
@csrf_exempt
def upload_edited_image(request: WSGIRequest) -> JsonResponse:
    pass

# TODO: Get image id from DB and update session token on each user POST, GET, PUT, DELETE requests
# update_session(request, _id=)