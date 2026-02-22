from django import template

register = template.Library()

@register.simple_tag(takes_context=True, name='get_parameters')
def get_parameters(context):
    request = context['request']

    if not request.GET:
        return ""

    request_copy = request.GET.copy()

    if 'page' in request_copy:
        del request_copy['page']


    return request_copy.urlencode() + "&"