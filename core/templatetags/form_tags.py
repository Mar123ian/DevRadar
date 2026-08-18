from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})


@register.filter
def class_name(value):
    return value.__class__.__name__


@register.filter
def class_name(value):
    return value.__class__.__name__
