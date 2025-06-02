from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

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