from django import template
from django.template.defaultfilters import stringfilter, title

register = template.Library()

@register.filter(name='toupper')
@stringfilter
def toupper(value):
    """ Testing template filters. Replaces value with uppercase value """
    return value.upper()


