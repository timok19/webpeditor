from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.models.database.serializers import OriginalImageSerializer


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def original_image_api(request, _id=0):
    if request.method == 'GET':
        original_images = OriginalImage.objects.all()
        original_image_serializer = OriginalImageSerializer(original_images, many=True)

        return JsonResponse(original_image_serializer.data, safe=False)

    elif request.method == 'POST':
        original_image_data = JSONParser().parse(request)
        original_image_serializer = OriginalImageSerializer(data=original_image_data)

        if original_image_serializer.is_valid():
            original_image_serializer.save()

            return JsonResponse("Added to db successfully", safe=False)

        return JsonResponse("Failed to add into db", safe=False)

    elif request.method == 'PUT':
        original_image_data = JSONParser().parse(request)
        original_image = OriginalImage.objects.get(image_id=original_image_data['image_id'])
        original_image_serializer = OriginalImageSerializer(original_image, data=original_image_data)

        if original_image_serializer.is_valid():
            original_image_serializer.save()

            return JsonResponse("Updated db successfully", safe=False)

        return JsonResponse("Failed to update db", safe=False)

    elif request.method == 'DELETE':
        original_image = OriginalImage.objects.get(image_id=_id)
        original_image.delete()

        return JsonResponse("Deleted successfully", safe=False)

