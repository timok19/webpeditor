from typing import Any
from django import template
from django.template import Library

register: Library = template.Library()


@register.filter
def decode_exif_value(value: Any) -> str:
    return value.decode(errors="ignore") if isinstance(value, bytes) else str(value)
