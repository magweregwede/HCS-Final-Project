from django import template

register = template.Library()

@register.filter
def intspace(value):
    try:
        value = int(value)
        return '{:,}'.format(value).replace(',', ' ')
    except (ValueError, TypeError):
        return value