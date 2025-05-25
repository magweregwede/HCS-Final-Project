from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class TruckCompany(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("truckcompany_detail", kwargs={"pk": self.pk})


class Truck(models.Model):
    plate_number = models.CharField(max_length=7, unique=True)
    capacity_kg = models.FloatField()
    truck_company = models.ForeignKey(TruckCompany, on_delete=models.CASCADE, related_name="trucks")
    status = models.CharField(max_length=50, choices=[("Active", "Active"),("In Use", "In Use"),("Maintenance", "Maintenance")])

    def __str__(self):
        return f"{self.plate_number} - {self.truck_company.name}"

    def get_absolute_url(self):
        return reverse("truck_detail", kwargs={"pk": self.pk})
        

class Driver(models.Model):
    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=10, unique=True)
    assigned_truck = models.OneToOneField(
        Truck, on_delete=models.SET_NULL, null=True, blank=True,unique=True)
    contact = models.CharField(max_length=10)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("driver_detail", kwargs={"pk": self.pk})


class Route(models.Model):
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    distance_km = models.FloatField()
    estimated_time_min = models.IntegerField()

    def __str__(self):
        return f"{self.origin} => {self.destination}"
    
    def get_absolute_url(self):
        return reverse("route_detail", kwargs={"pk": self.pk})

class Trip(models.Model):
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name="trips")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="trips")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("Ongoing", "Ongoing"), ("Completed", "Completed")], default="Ongoing")
    clerk = models.ForeignKey("auth.User",on_delete=models.CASCADE)

    def get_driver_assigned_truck(self):
        try:
            return self.driver.assigned_truck
        except AttributeError:
            return None

    def __str__(self):
        return f"Trip {self.id} - {self.truck.plate_number} ({self.status})"
    
    def get_absolute_url(self):
        return reverse("trip_detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
        # Update status based on arrival time
        if self.arrival_time is not None:
            self.status = "Completed"
        super().save(*args, **kwargs)
        # Update all related TripRoutes after saving
        self.update_related_routes()

    def update_related_routes(self):
        """Update all related TripRoute actual_time_min values"""
        for trip_route in self.trip_routes.all():
            trip_route.calculate_actual_time()
            trip_route.save(update_fields=['actual_time_min'])

@receiver(post_save, sender=Trip)
def update_related_trip_routes(sender, instance, **kwargs):
    instance.update_related_routes()

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=[("Water", "Water"), ("Cordial", "Cordial"),("Juice","Juice")])
    description = models.TextField()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})


class TripProduct(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="trip_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50, choices=[("Pallets", "Pallets"), ("Cases", "Cases")])

    def __str__(self):
        return f"Trip {self.trip.id} - {self.product.name} [{self.quantity} {self.unit}]"
    
    def get_absolute_url(self):
        return reverse("tripproduct_detail", kwargs={"pk": self.pk})


class TripRoute(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="trip_routes")
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    actual_time_min = models.IntegerField(editable=True, null=True, blank=True)  # Auto-calculated field

    def calculate_actual_time(self):
        """Calculate and update the actual time in minutes"""
        if self.trip.arrival_time and self.trip.departure_time:
            time_difference = self.trip.arrival_time - self.trip.departure_time
            self.actual_time_min = int(time_difference.total_seconds() / 60)
        else:
            self.actual_time_min = None

    def save(self, *args, **kwargs):
        self.calculate_actual_time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Route {self.route.origin} => {self.route.destination} for Trip {self.trip.id}"

    def get_absolute_url(self):
        return reverse("triproute_detail", kwargs={"pk": self.pk})


class DriverLeaderboard(models.Model):
    driver_name = models.CharField(max_length=100)
    total_points = models.IntegerField(default=0)
    rank_1_count = models.IntegerField(default=0)  # Number of times ranked #1
    rank_2_count = models.IntegerField(default=0)  # Number of times ranked #2
    rank_3_count = models.IntegerField(default=0)  # Number of times ranked #3
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_points', '-rank_1_count', '-rank_2_count']
    
    def __str__(self):
        return f"{self.driver_name} - {self.total_points} points"

class MonthlyDriverRanking(models.Model):
    driver_name = models.CharField(max_length=100)
    month = models.DateField()  # First day of the month
    rank = models.IntegerField()  # 1, 2, or 3
    trips_completed = models.IntegerField()
    points_earned = models.IntegerField()
    
    class Meta:
        unique_together = ['driver_name', 'month']
        ordering = ['-month', 'rank']
    
    def __str__(self):
        return f"{self.driver_name} - {self.month.strftime('%B %Y')} - Rank {self.rank}"

