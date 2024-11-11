from django import template
from django.template import Library
from django.template.defaultfilters import stringfilter

register: Library = template.Library()


@register.filter
@stringfilter
def replace_with_space(value: str, arg):
    return value.replace(arg, " ")


@register.filter
def is_instance(value, class_name):
    return isinstance(value, eval(class_name))
