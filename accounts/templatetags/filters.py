from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter()
def has_group(user, group_name):
    # Safely handle None or AnonymousUser
    if not user or not user.is_authenticated:
        return False

    return user.groups.filter(name=group_name).exists()

@register.filter()
def has_service_in_favourites(user, service_id):
    return user.favourites.filter(id=service_id).exists()

@register.filter
def replace_chars(value):
    """Форматира число с интервали за хиляди и запетаи за дробна част"""
    if isinstance(value, str):
        parts = value.split(",")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            integer_part = int(parts[0])
            formatted_value = f"{integer_part:,}".replace(",", " ") + "," + parts[1]
            return formatted_value
    return value
