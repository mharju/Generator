from django import template

def foo(value):
    """ Testing template filters. Replaces value with string 'foo' """
    return "foo"

register = template.Library()
register.filter('foo', foo)


