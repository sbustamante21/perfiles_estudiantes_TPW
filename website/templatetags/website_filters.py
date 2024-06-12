from django import template

register = template.Library()

@register.filter
def attr(obj, field):
    return getattr(obj, field)