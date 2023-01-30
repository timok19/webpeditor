from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def service_worker(request):
    sw_path = settings.BASE_DIR / "static" / "js" / "sw.js"
    response = HttpResponse(open(sw_path).read(), content_type='application/javascript')
    return response
