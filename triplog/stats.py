from django.db.models import Sum, Avg, Count, F, Max, Q
from django.utils.timezone import now
from datetime import timedelta, datetime
from .models import Trip, TripRoute, Route, Driver, Truck

def get_trip_stats():
    stats = {}

    # Active deliveries (Ongoing trips)
    stats['active_deliveries'] = Trip.objects.filter(status="Ongoing").count()

    # Available drivers (Drivers without any ongoing trips)
    stats['available_drivers'] = Driver.objects.annotate(
        ongoing_trips=Count('trips', filter=Q(trips__status="Ongoing"))
    ).filter(ongoing_trips=0).count()

    # Total kilometers covered from completed trips
    stats['total_kilometres'] = TripRoute.objects.filter(
        trip__status="Completed"
    ).aggregate(total_distance=Sum('route__distance_km'))['total_distance'] or 0

    # Average actual time of completed trips
    stats['average_trip_time'] = TripRoute.objects.filter(
        trip__status="Completed", actual_time_min__isnull=False
    ).aggregate(avg_time=Avg('actual_time_min'))['avg_time'] or 0

    # Number of completed trips
    stats['completed_trips'] = Trip.objects.filter(status="Completed").count()

    # Number of ongoing trips
    stats['ongoing_trips'] = Trip.objects.filter(status="Ongoing").count()

     # Average number of trips per driver
    stats['avg_trips_per_driver'] = Trip.objects.values('driver').annotate(
        total_trips=Count('id')
    ).aggregate(avg=Avg('total_trips'))['avg'] or 0

    # Total number of trucks
    stats['total_trucks'] = Truck.objects.count()

    # Average number of trips per truck
    stats['avg_trips_per_truck'] = Trip.objects.values('truck').annotate(
        total_trips=Count('id')
    ).aggregate(avg=Avg('total_trips'))['avg'] or 0

    # Longest trip distance (in completed trips)
    stats['longest_trip_distance'] = TripRoute.objects.filter(
        trip__status="Completed"
    ).aggregate(longest_distance=Max('route__distance_km'))['longest_distance'] or 0

    # Longest trip time (in hrs)
    stats['longest_trip_time(hrs)'] = TripRoute.objects.filter(
        trip__status="Completed", actual_time_min__isnull=False
    ).aggregate(longest_time=Max('actual_time_min'))['longest_time']/60 or 0

    # Total number of completed trips
    total_completed_trips = Trip.objects.filter(status="Completed").count()

    # Number of trips completed within estimated time
    stats['trips_within_estimated_time'] = TripRoute.objects.filter(
        trip__status="Completed", actual_time_min__lte=F('route__estimated_time_min')
    ).count()

    # Number of delayed trips (actual time exceeds estimated time)
    stats['delayed_trips'] = TripRoute.objects.filter(
        trip__status="Completed", actual_time_min__gt=F('route__estimated_time_min')
    ).count()

    # On-time rate (percentage of trips completed within the estimated time)
    on_time_trips = stats['trips_within_estimated_time']
    stats['on_time_rate'] = (on_time_trips / total_completed_trips * 100) if total_completed_trips > 0 else 0

    # Percentage of delayed trips
    delayed_trips = stats['delayed_trips']
    stats['percentage_delayed_trips'] = (delayed_trips / total_completed_trips * 100) if total_completed_trips > 0 else 0

    # Driver with most completed trips
    top_driver = Trip.objects.filter(
        status="Completed"
    ).values('driver__name').annotate(
        completed_trips=Count('id')
    ).order_by('-completed_trips').first()
    stats['top_driver'] = {
        'name': top_driver['driver__name'] if top_driver else None,
        'completed_trips': top_driver['completed_trips'] if top_driver else 0
    }

    # Truck with most trips
    top_truck = Trip.objects.values('truck__plate_number').annotate(
        total_trips=Count('id')
    ).order_by('-total_trips').first()
    stats['top_truck'] = {
        'plate_number': top_truck['truck__plate_number'] if top_truck else None,
        'total_trips': top_truck['total_trips'] if top_truck else 0
    }

    # Average delay time (in minutes) for delayed trips
    stats['total_delayed_time'] = TripRoute.objects.filter(
        trip__status="Completed", actual_time_min__gt=F('route__estimated_time_min')
    ).aggregate(total_delay=Sum(F('actual_time_min') - F('route__estimated_time_min')))['total_delay'] or 0
    delayed_trip_count = TripRoute.objects.filter(
        trip__status="Completed", actual_time_min__gt=F('route__estimated_time_min')
    ).count()
    stats['average_delay_time'] = (stats['total_delayed_time'] / delayed_trip_count) if delayed_trip_count > 0 else 0

    # Average delay time (in hours) for delayed trips
    stats['total_delayed_time(hrs)'] = (stats['total_delayed_time'] / 60) if stats['total_delayed_time'] > 0 else 0
    stats['average_delay_time(hrs)'] = (stats['average_delay_time'] / 60) if stats['average_delay_time'] > 0 else 0

    # Trips by status
    trips_by_status = Trip.objects.values('status').annotate(
        count=Count('id')
    )
    stats['trips_by_status'] = {
        status['status']: status['count'] for status in trips_by_status
    }

    # Most frequent Destination
    stats['most_frequent_route'] = str(TripRoute.objects.filter(
        trip__status="Completed"
    ).values('route__destination').annotate(
        trip_count=Count('id')
    ).order_by('-trip_count').first())

     # Weekly stats
    one_week_ago = now() - timedelta(days=7)

    # Weekly completed trips
    stats['weekly_completed_trips'] = Trip.objects.filter(
        status="Completed", departure_time__gte=one_week_ago
    ).count()

    # Weekly ongoing trips
    stats['weekly_ongoing_trips'] = Trip.objects.filter(
        status="Ongoing", departure_time__gte=one_week_ago
    ).count()

    # Weekly total kilometers covered
    stats['weekly_total_kilometres'] = TripRoute.objects.filter(
        trip__status="Completed", trip__departure_time__gte=one_week_ago
    ).aggregate(total_distance=Sum('route__distance_km'))['total_distance'] or 0

    # Weekly average trip time
    stats['weekly_average_trip_time'] = TripRoute.objects.filter(
        trip__status="Completed", trip__departure_time__gte=one_week_ago, actual_time_min__isnull=False
    ).aggregate(avg_time=Avg('actual_time_min'))['avg_time'] or 0

    # Weekly delayed trips
    stats['weekly_delayed_trips'] = TripRoute.objects.filter(
        trip__status="Completed", trip__departure_time__gte=one_week_ago,
        actual_time_min__gt=F('route__estimated_time_min')
    ).count()

    # Weekly on-time rate (percentage of trips completed within the estimated time)
    weekly_on_time_trips = TripRoute.objects.filter(
        trip__status="Completed", trip__departure_time__gte=one_week_ago,
        actual_time_min__lte=F('route__estimated_time_min')
    ).count()
    weekly_total_completed_trips = Trip.objects.filter(
        status="Completed", departure_time__gte=one_week_ago
    ).count()
    stats['weekly_on_time_rate'] = (weekly_on_time_trips / weekly_total_completed_trips * 100) if weekly_total_completed_trips > 0 else 0

    # Weekly stats (Monday to Sunday)
    today = now().date() 
    # weekday() returns an integer Monday=0 through Sunday=6
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Convert to datetime with time=00:00 and time=23:59:59
    start_of_week_dt = datetime.combine(start_of_week, datetime.min.time())
    end_of_week_dt = datetime.combine(end_of_week, datetime.max.time())

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
    weekly_total_completed_trips = Trip.objects.filter(
        status="Completed",
        departure_time__range=(start_of_week_dt, end_of_week_dt)
    ).count()
    stats['weekly_on_time_rate'] = (
        (weekly_on_time_trips / weekly_total_completed_trips) * 100
        if weekly_total_completed_trips > 0 else 0
    )

    # Monthly stats
    one_month_ago = now() - timedelta(days=30)

    stats['monthly_completed_trips'] = Trip.objects.filter(
        status="Completed", departure_time__gte=one_month_ago
    ).count()

    stats['monthly_ongoing_trips'] = Trip.objects.filter(
        status="Ongoing", departure_time__gte=one_month_ago
    ).count()

    stats['monthly_total_kilometres'] = TripRoute.objects.filter(
        trip__status="Completed", trip__departure_time__gte=one_month_ago
    ).aggregate(total_distance=Sum('route__distance_km'))['total_distance'] or 0

    stats['monthly_average_trip_time'] = TripRoute.objects.filter(
        trip__status="Completed", trip__departure_time__gte=one_month_ago, actual_time_min__isnull=False
    ).aggregate(avg_time=Avg('actual_time_min'))['avg_time'] or 0

    stats['monthly_delayed_trips'] = TripRoute.objects.filter(
        trip__status="Completed", trip__departure_time__gte=one_month_ago,
        actual_time_min__gt=F('route__estimated_time_min')
    ).count()

    monthly_on_time_trips = TripRoute.objects.filter(
        trip__status="Completed", trip__departure_time__gte=one_month_ago,
        actual_time_min__lte=F('route__estimated_time_min')
    ).count()
    monthly_total_completed_trips = Trip.objects.filter(
        status="Completed", departure_time__gte=one_month_ago
    ).count()
    stats['monthly_on_time_rate'] = (monthly_on_time_trips / monthly_total_completed_trips * 100) if monthly_total_completed_trips > 0 else 0

    # Monthly stats (current calendar month)
    start_of_month = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # end_of_month is optional if you want to limit exactly to the month,
    # but typically you can go up to 'now()'. If needed, you could do:
    # _, last_day = calendar.monthrange(start_of_month.year, start_of_month.month)
    # end_of_month = start_of_month.replace(day=last_day, hour=23, minute=59, second=59)
    # For simplicity, we’ll just go from start_of_month to now().
    end_of_month = now()

    stats['monthly_completed_trips'] = Trip.objects.filter(
        status="Completed",
        departure_time__range=(start_of_month, end_of_month)
    ).count()

    stats['monthly_ongoing_trips'] = Trip.objects.filter(
        status="Ongoing",
        departure_time__range=(start_of_month, end_of_month)
    ).count()

    stats['monthly_total_kilometres'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_month, end_of_month)
    ).aggregate(total_distance=Sum('route__distance_km'))['total_distance'] or 0

    stats['monthly_average_trip_time'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_month, end_of_month),
        actual_time_min__isnull=False
    ).aggregate(avg_time=Avg('actual_time_min'))['avg_time'] or 0

    stats['monthly_delayed_trips'] = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_month, end_of_month),
        actual_time_min__gt=F('route__estimated_time_min')
    ).count()

    monthly_on_time_trips = TripRoute.objects.filter(
        trip__status="Completed",
        trip__departure_time__range=(start_of_month, end_of_month),
        actual_time_min__lte=F('route__estimated_time_min')
    ).count()
    monthly_total_completed_trips = Trip.objects.filter(
        status="Completed",
        departure_time__range=(start_of_month, end_of_month)
    ).count()
    stats['monthly_on_time_rate'] = (
        (monthly_on_time_trips / monthly_total_completed_trips) * 100
        if monthly_total_completed_trips > 0 else 0
    )

    # Most frequent route in the past month
    most_frequent_monthly_route = TripRoute.objects.filter(
        trip__status="Completed", trip__departure_time__gte=one_month_ago
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

    # Top 3 monthly drivers with completed trips
    top_monthly_drivers = Trip.objects.filter(
        status="Completed", departure_time__gte=one_month_ago
    ).values(
        'driver__name', 'driver__assigned_truck__truck_company__name'
    ).annotate(
        completed_trips=Count('id')
    ).order_by('-completed_trips')[:3]

    stats['top_monthly_drivers'] = [
        f"{driver['driver__name']} ({driver['completed_trips']} trips) - {driver['driver__assigned_truck__truck_company__name'] or 'No Company'}"
        for driver in top_monthly_drivers
    ]

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

    top_monthly_drivers = Trip.objects.filter(
        status="Completed",
        departure_time__range=(start_of_month, end_of_month)
    ).values(
        'driver__name', 'driver__assigned_truck__truck_company__name'
    ).annotate(
        completed_trips=Count('id')
    ).order_by('-completed_trips')[:3]

    stats['top_monthly_drivers'] = [
        f"{driver['driver__name']} ({driver['completed_trips']} trips) - {driver['driver__assigned_truck__truck_company__name'] or 'No Company'}"
        for driver in top_monthly_drivers
    ]

    return stats
