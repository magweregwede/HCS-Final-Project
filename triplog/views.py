from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
import csv
from .models import Trip, TripProduct, Product, Driver, Truck
from .serializers import TripSerializer, TripProductSerializer, ProductSerializer, DriverSerializer, TruckSerializer

# 🚀 List all trips or create a new trip
class TripListCreateView(generics.ListCreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

# 🚀 Retrieve, update, or delete a single trip
class TripDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

# 🚀 List all products in a specific trip
class TripProductsView(generics.ListAPIView):
    serializer_class = TripProductSerializer

    def get_queryset(self):
        trip_id = self.kwargs['trip_id']
        return TripProduct.objects.filter(trip_id=trip_id)

# 🚀 List all trips by a specific driver
class DriverTripsView(generics.ListAPIView):
    serializer_class = TripSerializer

    def get_queryset(self):
        driver_id = self.kwargs['driver_id']
        return Trip.objects.filter(driver_id=driver_id)

# 🚀 List all trips for a specific truck
class TruckTripsView(generics.ListAPIView):
    serializer_class = TripSerializer

    def get_queryset(self):
        truck_id = self.kwargs['truck_id']
        return Trip.objects.filter(truck_id=truck_id)

# 🚀 List trips by status (Ongoing, Completed)
class TripsByStatusView(generics.ListAPIView):
    serializer_class = TripSerializer

    def get_queryset(self):
        status = self.kwargs['status']
        return Trip.objects.filter(status=status)

# 🚀 Export trips data to CSV
@api_view(['GET'])
def export_trips_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="trips.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Trip ID", "Truck", "Driver", "Departure Time", "Arrival Time", "Status"])
    
    trips = Trip.objects.all()
    for trip in trips:
        writer.writerow([trip.id, trip.truck.plate_number, trip.driver.name, trip.departure_time, trip.arrival_time, trip.status])

    return response

# Create your views here.
