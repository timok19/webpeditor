from typing import Any
from django import template

register = template.Library()


@register.filter
def decode_exif_value(value: Any, encoding="utf-8"):
    if isinstance(value, bytes):
        value = value.decode(encoding, errors="ignore")
    return value
