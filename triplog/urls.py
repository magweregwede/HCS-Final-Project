from django.urls import path
from .views import TripListCreateView, TripDetailView, TripProductsView,DriverTripsView, TruckTripsView, TripsByStatusView, export_trips_csv

urlpatterns = [
    path('trips/', TripListCreateView.as_view(), name='trip-list-create'),
    path('trips/<str:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('trips/<str:trip_id>/products/', TripProductsView.as_view(), name='trip-products'),
    path('drivers/<str:driver_id>/trips/', DriverTripsView.as_view(), name='driver-trips'),
    path('trucks/<str:truck_id>/trips/', TruckTripsView.as_view(), name='truck-trips'),
    path('trips/status/<str:status>/', TripsByStatusView.as_view(), name='trips-by-status'),
    path('export/trips/', export_trips_csv, name='export-trips-csv'),
]