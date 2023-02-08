from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render


def service_worker(request):
    sw_path = settings.BASE_DIR / "static" / "js" / "sw.js"

    return HttpResponse(open(sw_path).read(), content_type='application/javascript')
