from django.db.models import Sum, Avg, Count, F, Max
from .models import Trip, TripRoute, Route, Driver, Truck

def get_trip_stats():
    stats = {}

    # Active deliveries (Ongoing trips)
    stats['active_deliveries'] = Trip.objects.filter(status="Ongoing").count()

    # Available drivers (Drivers without any ongoing trips)
    stats['available_drivers'] = Driver.objects.annotate(
        ongoing_trips=Count('trips', filter=F('trips__status') == "Ongoing")
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

    return stats
