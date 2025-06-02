import csv
import os
from datetime import datetime, timedelta, date
from django.conf import settings
from django.db.models import Sum, Avg, Count, F, Max, Q
from django.utils.timezone import now, make_aware
from .models import Trip, TripRoute, Route, Driver, Truck

def get_previous_week_stats():
    """Get stats from the previous week using historical CSV data"""
    csv_file_path = os.path.join(settings.BASE_DIR, 'reports/historical_trip_stats_full.csv')
    
    if not os.path.exists(csv_file_path):
        return {}
    
    # Calculate previous week date range (Monday to Sunday)
    today = now().date()
    current_week_start = today - timedelta(days=today.weekday())  # Current Monday
    previous_week_start = current_week_start - timedelta(days=7)  # Previous Monday
    previous_week_end = previous_week_start + timedelta(days=6)   # Previous Sunday
    
    previous_week_stats = {}
    
    try:
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row['period_type'] == 'weekly' and 
                    row['period_start'] == previous_week_start.strftime('%Y-%m-%d') and
                    row['period_end'] == previous_week_end.strftime('%Y-%m-%d')):
                    
                    # Convert string values to appropriate types
                    previous_week_stats = {
                        'completed_trips': int(row['completed_trips']) if row['completed_trips'] else 0,
                        'ongoing_trips': int(row['ongoing_trips']) if row['ongoing_trips'] else 0,
                        'total_kilometres': float(row['total_kilometres']) if row['total_kilometres'] else 0,
                        'average_trip_time': float(row['average_trip_time']) if row['average_trip_time'] else 0,
                        'delayed_trips': int(row['delayed_trips']) if row['delayed_trips'] else 0,
                        'on_time_rate': float(row['on_time_rate']) if row['on_time_rate'] else 0,
                        'available_drivers': int(row['available_drivers']) if row['available_drivers'] else 0,
                        'active_deliveries': int(row['active_deliveries']) if row['active_deliveries'] else 0,
                    }
                    break
    except Exception as e:
        print(f"Error reading historical stats: {e}")
    
    return previous_week_stats

def get_previous_month_stats():
    """Get stats from the previous month using historical CSV data"""
    csv_file_path = os.path.join(settings.BASE_DIR, 'historical_trip_stats_full.csv')
    
    if not os.path.exists(csv_file_path):
        return {}
    
    # Calculate previous month date
    today = now().date()
    first_of_current_month = today.replace(day=1)
    
    if first_of_current_month.month == 1:
        previous_month_start = first_of_current_month.replace(year=first_of_current_month.year - 1, month=12)
    else:
        previous_month_start = first_of_current_month.replace(month=first_of_current_month.month - 1)
    
    # Calculate end of previous month
    if previous_month_start.month == 12:
        next_month = previous_month_start.replace(year=previous_month_start.year + 1, month=1)
    else:
        next_month = previous_month_start.replace(month=previous_month_start.month + 1)
    
    previous_month_end = next_month - timedelta(days=1)
    
    previous_month_stats = {}
    
    try:
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row['period_type'] == 'monthly' and 
                    row['period_start'] == previous_month_start.strftime('%Y-%m-%d') and
                    row['period_end'] == previous_month_end.strftime('%Y-%m-%d')):
                    
                    previous_month_stats = {
                        'monthly_on_time_rate': float(row['monthly_on_time_rate']) if row['monthly_on_time_rate'] else 0,
                        'monthly_total_kilometres': float(row['monthly_total_kilometres']) if row['monthly_total_kilometres'] else 0,
                    }
                    break
    except Exception as e:
        print(f"Error reading historical monthly stats: {e}")
    
    return previous_month_stats

def calculate_change(current_value, previous_value):
    """Calculate percentage change between current and previous values"""
    if previous_value == 0:
        return 100 if current_value > 0 else 0
    
    change = ((current_value - previous_value) / previous_value) * 100
    return round(change, 1)

def get_change_indicator(change):
    """Get appropriate indicator for the change"""
    if change > 0:
        return "↗"  # Up arrow
    elif change < 0:
        return "↘"  # Down arrow
    else:
        return "→"  # Right arrow (no change)

def get_change_class(change):
    """Get CSS class for styling the change"""
    if change > 0:
        return "text-success"  # Green for positive
    elif change < 0:
        return "text-danger"   # Red for negative
    else:
        return "text-muted"    # Gray for no change

def get_trip_stats():
    """Get comprehensive trip statistics with comparisons"""
    # Get current week stats
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    start_of_week_dt = make_aware(datetime.combine(start_of_week, datetime.min.time()))
    end_of_week_dt = make_aware(datetime.combine(end_of_week, datetime.max.time()))
    
    # Get current month stats
    start_of_month = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = now()
    
    stats = {}
    
    # Current week stats
    stats['weekly_completed_trips'] = Trip.objects.filter(
        status="Completed",
        departure_time__range=(start_of_week_dt, end_of_week_dt)
    ).count()
    
    stats['weekly_ongoing_trips'] = Trip.objects.filter(
        status="Ongoing",
        departure_time__range=(start_of_week_dt, end_of_week_dt)
    ).count()
    
    stats['weekly_total_kilometres'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_week_dt, end_of_week_dt)
    ).aggregate(total_distance=Sum('route__distance_km'))['total_distance'] or 0
    
    stats['weekly_average_trip_time'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_week_dt, end_of_week_dt),
        actual_time_min__isnull=False
    ).aggregate(avg_time=Avg('actual_time_min'))['avg_time'] or 0
    
    stats['weekly_delayed_trips'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_week_dt, end_of_week_dt),
        actual_time_min__gt=F('route__estimated_time_min')
    ).count()
    
    weekly_on_time_trips = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_week_dt, end_of_week_dt),
        actual_time_min__lte=F('route__estimated_time_min')
    ).count()
    weekly_total_completed_trips = stats['weekly_completed_trips']
    stats['weekly_on_time_rate'] = (
        (weekly_on_time_trips / weekly_total_completed_trips) * 100
        if weekly_total_completed_trips > 0 else 0
    )
    
    # Updated available drivers calculation: exclude both drivers on active deliveries AND unavailable drivers
    try:
        from drivers.models import DriverAvailability
        
        # Get drivers that are marked as available in the availability system
        available_driver_ids = DriverAvailability.objects.filter(
            is_available=True
        ).values_list('triplog_driver_id', flat=True)
        
        # From those available drivers, exclude ones with ongoing trips
        stats['available_drivers'] = Driver.objects.filter(
            id__in=available_driver_ids
        ).annotate(
            ongoing_trips=Count('trips', filter=Q(trips__status="Ongoing"))
        ).filter(ongoing_trips=0).count()
        
    except ImportError:
        # Fallback if drivers app is not available - just exclude drivers with ongoing trips
        stats['available_drivers'] = Driver.objects.annotate(
            ongoing_trips=Count('trips', filter=Q(trips__status="Ongoing"))
        ).filter(ongoing_trips=0).count()
    
    stats['active_deliveries'] = Trip.objects.filter(status="Ongoing").count()
    
    # Monthly stats
    stats['monthly_completed_trips'] = Trip.objects.filter(
        status="Completed",
        departure_time__range=(start_of_month, end_of_month)
    ).count()
    
    stats['monthly_ongoing_trips'] = Trip.objects.filter(
        status="Ongoing",
        departure_time__range=(start_of_month, end_of_month)
    ).count()
    
    stats['monthly_on_time_rate'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_month, end_of_month),
        actual_time_min__lte=F('route__estimated_time_min')
    ).count()
    
    monthly_total_completed = Trip.objects.filter(
        status="Completed",
        departure_time__range=(start_of_month, end_of_month)
    ).count()
    
    if monthly_total_completed > 0:
        stats['monthly_on_time_rate'] = (stats['monthly_on_time_rate'] / monthly_total_completed) * 100
    else:
        stats['monthly_on_time_rate'] = 0
    
    stats['monthly_total_kilometres'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_month, end_of_month)
    ).aggregate(total_distance=Sum('route__distance_km'))['total_distance'] or 0
    
    # Top monthly route
    most_frequent_monthly_route = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_month, end_of_month)
    ).values(
        'route__origin', 'route__destination'
    ).annotate(
        trip_count=Count('id')
    ).order_by('-trip_count').first()

    stats['most_frequent_monthly_route'] = (
        f"{most_frequent_monthly_route['route__origin']} to {most_frequent_monthly_route['route__destination']} "
        f"({most_frequent_monthly_route['trip_count']} trips)"
        if most_frequent_monthly_route else "No data"
    )
    
    # Top monthly drivers
    top_drivers = Trip.objects.filter(
        status="Completed",
        departure_time__range=(start_of_month, end_of_month)
    ).values('driver__name').annotate(
        trips=Count('id')
    ).order_by('-trips')[:3]
    
    stats['top_monthly_drivers'] = [
        {'name': driver['driver__name'], 'trips': driver['trips']}
        for driver in top_drivers
    ]
    
    # Get previous week and month stats for comparison
    previous_stats = get_previous_week_stats()
    previous_month_stats = get_previous_month_stats()
    
    # Calculate changes and add to stats
    current_stats_for_comparison = {
        'completed_trips': stats['weekly_completed_trips'],
        'ongoing_trips': stats['weekly_ongoing_trips'],
        'total_kilometres': stats['weekly_total_kilometres'],
        'average_trip_time': stats['weekly_average_trip_time'],
        'delayed_trips': stats['weekly_delayed_trips'],
        'on_time_rate': stats['weekly_on_time_rate'],
        'available_drivers': stats['available_drivers'],
        'active_deliveries': stats['active_deliveries'],
    }
    
    # Add change information to stats
    for key, current_value in current_stats_for_comparison.items():
        previous_value = previous_stats.get(key, 0)
        change = calculate_change(current_value, previous_value)
        
        stats[f'{key}_change'] = change
        stats[f'{key}_change_indicator'] = get_change_indicator(change)
        stats[f'{key}_change_class'] = get_change_class(change)
        stats[f'{key}_previous'] = previous_value
    
    # Monthly change calculations
    monthly_stats_for_comparison = {
        'monthly_on_time_rate': stats['monthly_on_time_rate'],
        'monthly_total_kilometres': stats['monthly_total_kilometres'],
    }
    
    for key, current_value in monthly_stats_for_comparison.items():
        previous_value = previous_month_stats.get(key, 0)
        change = calculate_change(current_value, previous_value)
        
        stats[f'{key}_change'] = change
        stats[f'{key}_change_indicator'] = get_change_indicator(change)
        stats[f'{key}_change_class'] = get_change_class(change)
        stats[f'{key}_previous'] = previous_value
    
    return stats
