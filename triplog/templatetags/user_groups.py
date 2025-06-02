from django import template

register = template.Library()

@register.filter
def is_in_group(user, group_name):
    """Check if user is in a specific group"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()

@register.filter
def is_clerk(user):
    """Check if user is a clerk"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='clerks').exists()

@register.filter
def is_manager(user):
    """Check if user is a manager"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='managers').exists()

@register.filter
def is_driver(user):
    """Check if user is a driver"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='drivers').exists()

@register.filter
def is_clerk_or_manager(user):
    """Check if user is clerk or manager"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=['clerks', 'managers']).exists()

@register.filter
def has_availability_access(user):
    """Check if user can access driver availability"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=['drivers', 'clerks', 'managers']).exists()

@register.filter
def has_reporting_access(user):
    """Check if user can access reporting"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=['drivers', 'clerks', 'managers']).exists()