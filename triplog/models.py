from django.db import models
from django.conf import settings

# Create your models here.

class TruckCompany(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Truck(models.Model):
    plate_number = models.CharField(max_length=7, unique=True)
    capacity_kg = models.FloatField()
    truck_company = models.ForeignKey(TruckCompany, on_delete=models.CASCADE, related_name="trucks")
    status = models.CharField(max_length=50, choices=[("Active", "Active"),("In Use", "In Use"),("Maintenance", "Maintenance")])

    def __str__(self):
        return f"{self.plate_number} - {self.truck_company.name}"
        

class Driver(models.Model):
    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=10, unique=True)
    assigned_truck = models.OneToOneField(
        Truck, on_delete=models.SET_NULL, null=True, blank=True)
    contact = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Route(models.Model):
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    distance_km = models.FloatField()
    estimated_time_min = models.IntegerField()

    def __str__(self):
        return f"{self.origin} => {self.destination}"


class Trip(models.Model):
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name="trips")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="trips")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("Ongoing", "Ongoing"), ("Completed", "Completed")], default="Ongoing")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Trip {self.id} - {self.truck.plate_number} ({self.status})"


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=[("Water", "Water"), ("Cordial", "Cordial"),("Juice","Juice")])
    description = models.TextField()

    def __str__(self):
        return self.name


class TripProduct(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="trip_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50, choices=[("Pallets", "Pallets"), ("Cases", "Cases")])

    def __str__(self):
        return f"{self.product.name} ({self.quantity} {self.unit}) for Trip {self.trip.id}"


class TripRoute(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="trip_routes")
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    actual_time_min = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Route {self.route.origin} => {self.route.destination} for Trip {self.trip.id}"
