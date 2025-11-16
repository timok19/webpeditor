from typing import Union
from django.contrib import admin, messages
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.urls import URLPattern, path
from django.utils.html import format_html
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _

from api.infrastructure.database.models import APIKey
from common.core.types import Pair


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin[APIKey]):
    list_display = ("email", "key_hash", "created_at", "generate_new_key")
    list_filter = ("email", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("key_hash", "created_at")

    def get_urls(self) -> list[URLPattern]:
        view = self.admin_site.admin_view(self.generate_new_key_view)
        return [path("generate-key/<int:api_key_id>/", view, name="generate-api-key")] + super().get_urls()

    def save_model(self, request: HttpRequest, obj: APIKey, form: ModelForm, change: bool) -> None:
        if change:
            super().save_model(request, obj, form, change)
            return None

        api_key, key_hash = self.__create_api_key_and_hash()
        obj.key_hash = key_hash
        super().save_model(request, obj, form, change)
        self.__notify_api_key_created(request, obj.email, api_key)
        return None

    def generate_new_key_view(self, request: HttpRequest, api_key_id: int) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
        api_key, key_hash = self.__create_api_key_and_hash()
        api_key_obj = APIKey.objects.get(pk=api_key_id)
        api_key_obj.key_hash = key_hash
        api_key_obj.save()
        self.__notify_api_key_created(request, api_key_obj.email, api_key)
        return redirect("admin:webpeditor_app_apikey_changelist")

    @staticmethod
    def generate_new_key(obj: APIKey) -> SafeText:
        return format_html('<a class="button" href="/admin/webpeditor_app/apikey/generate-key/{}/">{}</a>', obj.pk, _("Generate New Key"))

    @staticmethod
    def __create_api_key_and_hash() -> Pair[str, str]:
        api_key = APIKey.create_api_key()
        api_key_hash = APIKey.hash_api_key(api_key)
        return Pair[str, str](api_key, api_key_hash)

    @staticmethod
    def __notify_api_key_created(request: HttpRequest, email: str, api_key: str) -> None:
        message = _("New API key generated for") + f' "{email}": {api_key} ' + _("(Save this key, it won't be shown again)")
        messages.success(request, message)
        return None
