from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponseForbidden

def is_clerk(user):
    """Check if user is in clerks group"""
    return user.groups.filter(name='clerks').exists()

def is_manager(user):
    """Check if user is in managers group"""
    return user.groups.filter(name='managers').exists()

def is_driver(user):
    """Check if user is in drivers group"""
    return user.groups.filter(name='drivers').exists()

def is_clerk_or_manager(user):
    """Check if user is clerk or manager"""
    return is_clerk(user) or is_manager(user)

def is_driver_clerk_or_manager(user):
    """Check if user is driver, clerk, or manager"""
    return is_driver(user) or is_clerk(user) or is_manager(user)

class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for manager-only views"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return is_manager(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('dashboard')

class ClerkOrManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for clerk or manager views"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return is_clerk_or_manager(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('dashboard')

class LogisticsReadOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for logistics partners - clerks can only view"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return is_clerk_or_manager(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('dashboard')

class LogisticsEditMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for logistics partners editing - managers only"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return is_manager(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('dashboard')

class DriverClerkManagerMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for views accessible to drivers, clerks, and managers"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return is_driver_clerk_or_manager(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('dashboard')

# New mixins for Routes and Products management

class RouteViewMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for viewing routes - clerks and managers can view"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return is_clerk_or_manager(self.request.user)
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "You don't have permission to view routes. Only clerks and managers can access this page.")
            return redirect('dashboard')
        else:
            messages.warning(self.request, "Please log in to access this page.")
            return redirect('login')

class RouteEditMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for editing routes - managers only"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return is_manager(self.request.user)
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            if is_clerk(self.request.user):
                messages.warning(self.request, "Only managers can edit routes. You have read-only access.")
                return redirect('route_list')
            else:
                messages.error(self.request, "You don't have permission to edit routes. Only managers can make changes.")
                return redirect('dashboard')
        else:
            messages.warning(self.request, "Please log in to access this page.")
            return redirect('login')

class ProductViewMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for viewing products - clerks and managers can view"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return is_clerk_or_manager(self.request.user)
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "You don't have permission to view products. Only clerks and managers can access this page.")
            return redirect('dashboard')
        else:
            messages.warning(self.request, "Please log in to access this page.")
            return redirect('login')

class ProductEditMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin for editing products - managers only"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return is_manager(self.request.user)
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            if is_clerk(self.request.user):
                messages.warning(self.request, "Only managers can edit products. You have read-only access.")
                return redirect('product_list')
            else:
                messages.error(self.request, "You don't have permission to edit products. Only managers can make changes.")
                return redirect('dashboard')
        else:
            messages.warning(self.request, "Please log in to access this page.")
            return redirect('login')

# Decorator versions for function-based views

def clerk_or_manager_required(view_func):
    """Decorator for views that require clerk or manager permissions"""
    @login_required
    @user_passes_test(is_clerk_or_manager)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper

def manager_required(view_func):
    """Decorator for views that require manager permissions"""
    @login_required
    @user_passes_test(is_manager)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper

def route_view_required(view_func):
    """Decorator for route viewing - clerks and managers"""
    @login_required
    @user_passes_test(is_clerk_or_manager)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper

def route_edit_required(view_func):
    """Decorator for route editing - managers only"""
    @login_required
    @user_passes_test(is_manager)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper

def product_view_required(view_func):
    """Decorator for product viewing - clerks and managers"""
    @login_required
    @user_passes_test(is_clerk_or_manager)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper

def product_edit_required(view_func):
    """Decorator for product editing - managers only"""
    @login_required
    @user_passes_test(is_manager)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper