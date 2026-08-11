
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def pending_email(context):
    request = context["request"]
    return request.session.get(
        "pending_verification_email"
    )