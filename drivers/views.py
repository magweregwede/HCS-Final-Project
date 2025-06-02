from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import DriverAvailability

def is_clerk(user):
    """Check if user is in clerks group"""
    return user.groups.filter(name='clerks').exists()

def is_driver(user):
    """Check if user is in drivers group"""
    return user.groups.filter(name='drivers').exists()

@login_required
def driver_availability_dashboard(request):
    """Main dashboard for driver availability"""
    user_is_clerk = is_clerk(request.user)
    user_is_driver = is_driver(request.user)
    
    if not (user_is_clerk or user_is_driver):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    # Get all driver availabilities
    availabilities = DriverAvailability.objects.select_related(
        'user', 'triplog_driver'
    ).order_by('triplog_driver__name')
    
    # If user is a driver, get their specific availability
    driver_availability = None
    if user_is_driver:
        try:
            driver_availability = DriverAvailability.objects.get(user=request.user)
        except DriverAvailability.DoesNotExist:
            messages.warning(request, "No availability record found for your account. Please contact an administrator.")
    
    context = {
        'availabilities': availabilities,
        'driver_availability': driver_availability,
        'is_clerk': user_is_clerk,
        'is_driver': user_is_driver,
        'available_count': availabilities.filter(is_available=True).count(),
        'unavailable_count': availabilities.filter(is_available=False).count(),
    }
    
    return render(request, 'availability/dashboard.html', context)

@login_required
@user_passes_test(is_driver)
def update_driver_availability(request):
    """Allow drivers to update their own availability"""
    try:
        driver_availability = DriverAvailability.objects.get(user=request.user)
    except DriverAvailability.DoesNotExist:
        messages.error(request, "No availability record found for your account.")
        return redirect('drivers:availability_dashboard')
    
    if request.method == 'POST':
        is_available = request.POST.get('is_available') == 'true'
        notes = request.POST.get('notes', '').strip()
        
        driver_availability.is_available = is_available
        driver_availability.notes = notes
        driver_availability.save()
        
        status = "available" if is_available else "unavailable"
        messages.success(request, f"Your availability has been updated to {status}.")
        
        return redirect('drivers:availability_dashboard')
    
    context = {
        'driver_availability': driver_availability,
    }
    
    return render(request, 'availability/update.html', context)

@login_required
@user_passes_test(is_clerk)
@csrf_exempt
def toggle_driver_availability(request):
    """AJAX endpoint for clerks to toggle driver availability"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            driver_id = data.get('driver_id')
            
            driver_availability = get_object_or_404(DriverAvailability, id=driver_id)
            driver_availability.is_available = not driver_availability.is_available
            driver_availability.save()
            
            return JsonResponse({
                'success': True,
                'is_available': driver_availability.is_available,
                'message': f"{driver_availability.driver_name} is now {'available' if driver_availability.is_available else 'unavailable'}"
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating availability: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def get_available_drivers_api(request):
    """API endpoint to get available drivers for forms"""
    available_drivers = DriverAvailability.objects.filter(
        is_available=True
    ).select_related('triplog_driver')
    
    drivers_data = [
        {
            'id': av.triplog_driver.id,
            'name': av.triplog_driver.name,
            'contact': av.triplog_driver.contact,
            'assigned_truck': str(av.triplog_driver.assigned_truck) if av.triplog_driver.assigned_truck else None
        }
        for av in available_drivers
    ]
    
    return JsonResponse({'drivers': drivers_data})
