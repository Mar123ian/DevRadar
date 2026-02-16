from django import template

register = template.Library()

@register.simple_tag(takes_context=True, name='get_parameters')
def get_parameters(context):
    request = context['request']

    if not request.GET:
        return ""

    return request.GET.urlencode() + "&"