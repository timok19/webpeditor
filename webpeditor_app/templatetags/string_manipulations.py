from typing import Any
from django import template
from django.template import Library

register: Library = template.Library()


@register.filter
def is_instance(value: Any, class_name: str) -> bool:
    return isinstance(value, eval(class_name))
