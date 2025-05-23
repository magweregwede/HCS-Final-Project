from django.db.models import Sum, Avg, Count, F, Max, Q
from django.utils.timezone import now, make_aware
from datetime import datetime, timedelta, date
from .models import Trip, TripRoute, Route, Driver, Truck

def get_stats_for_date_range(start_date, end_date=None):
    """Get comprehensive statistics for a specific date range"""
    if end_date is None:
        end_date = now()
    
    # Convert dates to datetime if they aren't already
    if isinstance(start_date, date):
        start_date = make_aware(datetime.combine(start_date, datetime.min.time()))
    if isinstance(end_date, date):
        end_date = make_aware(datetime.combine(end_date, datetime.max.time()))
    
    stats = {
        'period_start': start_date.date(),
        'period_end': end_date.date(),
    }
    
    # Base filter for all trip queries
    trip_filter = Q(departure_time__range=(start_date, end_date))
    completed_filter = trip_filter & Q(status="Completed")
    ongoing_filter = trip_filter & Q(status="Ongoing")
    
    # Active deliveries (Ongoing trips)
    stats['active_deliveries'] = Trip.objects.filter(ongoing_filter).count()

    # Available drivers (Drivers without any ongoing trips)
    stats['available_drivers'] = Driver.objects.annotate(
        ongoing_trips=Count('trips', filter=Q(trips__status="Ongoing", trips__departure_time__range=(start_date, end_date)))
    ).filter(ongoing_trips=0).count()

    # Total kilometers covered from completed trips
    stats['total_kilometres'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_date, end_date)
    ).aggregate(total_distance=Sum('route__distance_km'))['total_distance'] or 0

    # Average actual time of completed trips
    stats['average_trip_time'] = TripRoute.objects.filter(
        trip__status="Completed", 
        trip__departure_time__range=(start_date, end_date),
        actual_time_min__isnull=False
    ).aggregate(avg_time=Avg('actual_time_min'))['avg_time'] or 0

    # Number of completed trips
    stats['completed_trips'] = Trip.objects.filter(completed_filter).count()

    # Number of ongoing trips
    stats['ongoing_trips'] = Trip.objects.filter(ongoing_filter).count()

    # Average number of trips per driver
    stats['avg_trips_per_driver'] = Trip.objects.filter(
        departure_time__range=(start_date, end_date)
    ).values('driver').annotate(
        total_trips=Count('id')
    ).aggregate(avg=Avg('total_trips'))['avg'] or 0

    # Total number of trucks
    stats['total_trucks'] = Truck.objects.count()

    # Average number of trips per truck
    stats['avg_trips_per_truck'] = Trip.objects.filter(
        departure_time__range=(start_date, end_date)
    ).values('truck').annotate(
        total_trips=Count('id')
    ).aggregate(avg=Avg('total_trips'))['avg'] or 0

    # Longest trip distance (in completed trips)
    stats['longest_trip_distance'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_date, end_date)
    ).aggregate(longest_distance=Max('route__distance_km'))['longest_distance'] or 0

    # Longest trip time (in hrs)
    longest_time_min = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_date, end_date),
        actual_time_min__isnull=False
    ).aggregate(longest_time=Max('actual_time_min'))['longest_time'] or 0
    stats['longest_trip_time(hrs)'] = longest_time_min / 60 if longest_time_min else 0

    # Total number of completed trips
    total_completed_trips = stats['completed_trips']

    # Number of trips completed within estimated time
    stats['trips_within_estimated_time'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_date, end_date),
        actual_time_min__lte=F('route__estimated_time_min')
    ).count()

    # Number of delayed trips (actual time exceeds estimated time)
    stats['delayed_trips'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_date, end_date),
        actual_time_min__gt=F('route__estimated_time_min')
    ).count()

    # On-time rate (percentage of trips completed within the estimated time)
    on_time_trips = stats['trips_within_estimated_time']
    stats['on_time_rate'] = (on_time_trips / total_completed_trips * 100) if total_completed_trips > 0 else 0

    # Percentage of delayed trips
    delayed_trips = stats['delayed_trips']
    stats['percentage_delayed_trips'] = (delayed_trips / total_completed_trips * 100) if total_completed_trips > 0 else 0

    # Driver with most completed trips
    top_driver = Trip.objects.filter(completed_filter).values(
        'driver__name'
    ).annotate(
        completed_trips=Count('id')
    ).order_by('-completed_trips').first()
    stats['top_driver'] = {
        'name': top_driver['driver__name'] if top_driver else None,
        'completed_trips': top_driver['completed_trips'] if top_driver else 0
    }

    # Truck with most trips
    top_truck = Trip.objects.filter(
        departure_time__range=(start_date, end_date)
    ).values('truck__plate_number').annotate(
        total_trips=Count('id')
    ).order_by('-total_trips').first()
    stats['top_truck'] = {
        'plate_number': top_truck['truck__plate_number'] if top_truck else None,
        'total_trips': top_truck['total_trips'] if top_truck else 0
    }

    # Average delay time calculations
    delayed_stats = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_date, end_date),
        actual_time_min__gt=F('route__estimated_time_min')
    ).aggregate(
        total_delay=Sum(F('actual_time_min') - F('route__estimated_time_min')),
        count=Count('id')
    )
    
    stats['total_delayed_time'] = delayed_stats['total_delay'] or 0
    delayed_trip_count = delayed_stats['count'] or 0
    stats['average_delay_time'] = (stats['total_delayed_time'] / delayed_trip_count) if delayed_trip_count > 0 else 0
    stats['total_delayed_time(hrs)'] = stats['total_delayed_time'] / 60 if stats['total_delayed_time'] else 0
    stats['average_delay_time(hrs)'] = stats['average_delay_time'] / 60 if stats['average_delay_time'] else 0

    # Trips by status
    trips_by_status = Trip.objects.filter(
        departure_time__range=(start_date, end_date)
    ).values('status').annotate(
        count=Count('id')
    )
    stats['trips_by_status'] = {
        status['status']: status['count'] for status in trips_by_status
    }

    # Most frequent Destination
    most_frequent_route = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_date, end_date)
    ).values('route__origin', 'route__destination').annotate(
        trip_count=Count('id')
    ).order_by('-trip_count').first()
    stats['most_frequent_route'] = (
        f"{most_frequent_route['route__origin']} to {most_frequent_route['route__destination']}"
        if most_frequent_route else None
    )

    # Weekly stats (for the current week in the date range)
    # Calculate the Monday of the current week
    if end_date.date() - start_date.date() <= timedelta(days=7):
        # If the range is <= 7 days, treat it as a weekly report
        stats['weekly_completed_trips'] = stats['completed_trips']
        stats['weekly_ongoing_trips'] = stats['ongoing_trips']
        stats['weekly_total_kilometres'] = stats['total_kilometres']
        stats['weekly_average_trip_time'] = stats['average_trip_time']
        stats['weekly_delayed_trips'] = stats['delayed_trips']
        stats['weekly_on_time_rate'] = stats['on_time_rate']
    else:
        # For longer ranges, calculate the last 7 days
        week_start = end_date - timedelta(days=7)
        stats['weekly_completed_trips'] = Trip.objects.filter(
            status="Completed",
            departure_time__range=(week_start, end_date)
        ).count()
        stats['weekly_ongoing_trips'] = Trip.objects.filter(
            status="Ongoing",
            departure_time__range=(week_start, end_date)
        ).count()
        stats['weekly_total_kilometres'] = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(week_start, end_date)
        ).aggregate(total_distance=Sum('route__distance_km'))['total_distance'] or 0
        stats['weekly_average_trip_time'] = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(week_start, end_date),
            actual_time_min__isnull=False
        ).aggregate(avg_time=Avg('actual_time_min'))['avg_time'] or 0
        weekly_delayed = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(week_start, end_date),
            actual_time_min__gt=F('route__estimated_time_min')
        ).count()
        weekly_total = stats['weekly_completed_trips']
        stats['weekly_delayed_trips'] = weekly_delayed
        stats['weekly_on_time_rate'] = (
            (weekly_total - weekly_delayed) / weekly_total * 100 
            if weekly_total > 0 else 0
        )

    # Monthly stats (for the current month in the date range)
    if (end_date.year == start_date.year and end_date.month == start_date.month) or \
       (end_date - start_date <= timedelta(days=31)):
        # If within same month or <= 31 days, treat as monthly report
        stats['monthly_completed_trips'] = stats['completed_trips']
        stats['monthly_ongoing_trips'] = stats['ongoing_trips']
        stats['monthly_total_kilometres'] = stats['total_kilometres']
        stats['monthly_average_trip_time'] = stats['average_trip_time']
        stats['monthly_delayed_trips'] = stats['delayed_trips']
        stats['monthly_on_time_rate'] = stats['on_time_rate']
    else:
        # For longer ranges, calculate the last 30 days
        month_start = end_date - timedelta(days=30)
        stats['monthly_completed_trips'] = Trip.objects.filter(
            status="Completed",
            departure_time__range=(month_start, end_date)
        ).count()
        stats['monthly_ongoing_trips'] = Trip.objects.filter(
            status="Ongoing",
            departure_time__range=(month_start, end_date)
        ).count()
        stats['monthly_total_kilometres'] = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(month_start, end_date)
        ).aggregate(total_distance=Sum('route__distance_km'))['total_distance'] or 0
        stats['monthly_average_trip_time'] = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(month_start, end_date),
            actual_time_min__isnull=False
        ).aggregate(avg_time=Avg('actual_time_min'))['avg_time'] or 0
        monthly_delayed = TripRoute.objects.filter(
            trip__status="Completed",
            trip__departure_time__range=(month_start, end_date),
            actual_time_min__gt=F('route__estimated_time_min')
        ).count()
        monthly_total = stats['monthly_completed_trips']
        stats['monthly_delayed_trips'] = monthly_delayed
        stats['monthly_on_time_rate'] = (
            (monthly_total - monthly_delayed) / monthly_total * 100 
            if monthly_total > 0 else 0
        )

    # Most frequent route in the period
    most_frequent_monthly_route = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_date, end_date)
    ).values('route__origin', 'route__destination').annotate(
        trip_count=Count('id')
    ).order_by('-trip_count').first()
    stats['most_frequent_monthly_route'] = (
        f"{most_frequent_monthly_route['route__origin']} to {most_frequent_monthly_route['route__destination']}"
        if most_frequent_monthly_route else None
    )

    # Top 3 drivers in the period
    top_monthly_drivers = Trip.objects.filter(completed_filter).values(
        'driver__name', 'driver__assigned_truck__truck_company__name'
    ).annotate(
        completed_trips=Count('id')
    ).order_by('-completed_trips')[:3]
    stats['top_monthly_drivers'] = [
        f"{driver['driver__name']} ({driver['completed_trips']} trips)"
        for driver in top_monthly_drivers
    ] if top_monthly_drivers else []

    return stats

def generate_historical_stats(start_date=date(2024, 2, 1)):
    """Generate weekly and monthly stats from start_date to now"""
    end_date = now().date()
    current_date = start_date
    all_stats = []

    # Align the start date to the nearest Monday
    if current_date.weekday() != 0:  # If not Monday
        current_date = current_date - timedelta(days=current_date.weekday())  # Move to the previous Monday

    # Generate stats
    while current_date <= end_date:
        # Calculate the start of the next month
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1, day=1)

        # Calculate the end of the current month
        month_end = min(next_month - timedelta(days=1), end_date)

        # Get monthly stats
        monthly_stats = get_stats_for_date_range(current_date, month_end)
        monthly_stats['period_type'] = 'monthly'
        all_stats.append(monthly_stats)

        # Generate weekly stats within this month
        week_start = current_date
        while week_start <= month_end:
            week_end = min(week_start + timedelta(days=6), month_end)  # End on Sunday or the end of the month

            # Get weekly stats
            weekly_stats = get_stats_for_date_range(week_start, week_end)
            weekly_stats['period_type'] = 'weekly'
            all_stats.append(weekly_stats)

            # Move to the next Monday
            week_start = week_end + timedelta(days=1)

        # Move to the next month
        current_date = next_month

    return all_stats