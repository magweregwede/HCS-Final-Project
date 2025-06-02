from django.db import models
from django.contrib.auth.models import User
from triplog.models import Driver as TriplogDriver

class DriverAvailability(models.Model):
    """Model to track driver availability and link to triplog Driver model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_availability')
    triplog_driver = models.OneToOneField(TriplogDriver, on_delete=models.CASCADE, related_name='availability')
    is_available = models.BooleanField(default=True, help_text="Whether the driver is currently available for trips")
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about availability status")
    
    class Meta:
        verbose_name = "Driver Availability"
        verbose_name_plural = "Driver Availabilities"
    
    def __str__(self):
        return f"{self.triplog_driver.name} - {'Available' if self.is_available else 'Unavailable'}"
    
    @property
    def driver_name(self):
        return self.triplog_driver.name
    
    @property
    def username(self):
        return self.user.username
