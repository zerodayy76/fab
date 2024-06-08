# custom_filters.py
from django import template

register = template.Library()

@register.filter
def int_range(value):
    return range(int(value))

@register.filter
def subtract(value, arg):
    return int(value) - int(arg)
