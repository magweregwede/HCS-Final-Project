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
    # stats['longest_trip_distance'] = TripRoute.objects.filter(
        # trip__status="Completed"
    # ).aggregate(longest_distance=max('route__distance_km'))['longest_distance'] or 0

    # Longest trip distance (in completed trips)
    stats['longest_trip_distance'] = TripRoute.objects.filter(
        trip__status="Completed"
    ).aggregate(longest_distance=Max('route__distance_km'))['longest_distance'] or 0

    # Longest trip time (in minutes)
    stats['longest_trip_time(hrs)'] = TripRoute.objects.filter(
        trip__status="Completed", actual_time_min__isnull=False
    ).aggregate(longest_time=Max('actual_time_min'))['longest_time']/60 or 0

    # Number of trips completed within estimated time
    stats['trips_within_estimated_time'] = TripRoute.objects.filter(
        trip__status="Completed", actual_time_min__lte=F('route__estimated_time_min')
    ).count()

    # Number of delayed trips (actual time exceeds estimated time)
    stats['delayed_trips'] = TripRoute.objects.filter(
        trip__status="Completed", actual_time_min__gt=F('route__estimated_time_min')
    ).count()

    return stats
