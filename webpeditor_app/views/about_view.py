from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "webpeditor_app/about.html"
