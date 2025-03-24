from django import template

register = template.Library()

@register.filter
def minutes_to_hours(minutes):
    if minutes is None:
        return "Trip NOT COMPLETE"  # Handle cases where the value is None
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m" if hours else f"{mins}m"