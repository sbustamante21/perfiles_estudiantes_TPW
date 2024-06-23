from django import template
from website.models import User


register = template.Library()

@register.filter
def attr(obj, field):
    return getattr(obj, field)

@register.filter
def display_role(value, field_name):
    if field_name == 'role' and isinstance(value, int):
        return dict(User.ROLE_CHOICES).get(value, "Unknown")
    return value