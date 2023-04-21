from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def replace_with_space(value: str, arg):
    return value.replace(arg, " ")


@register.filter
def is_instance(value, class_name):
    # TODO: Handle case, when exif data in dict

    return isinstance(value, eval(class_name))
