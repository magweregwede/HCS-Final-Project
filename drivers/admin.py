from django.contrib import admin
from .models import DriverAvailability

@admin.register(DriverAvailability)
class DriverAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['driver_name', 'username', 'is_available', 'last_updated']
    list_filter = ['is_available', 'last_updated']
    search_fields = ['user__username', 'triplog_driver__name']
    readonly_fields = ['last_updated']
    
    def driver_name(self, obj):
        return obj.triplog_driver.name
    driver_name.short_description = 'Driver Name'
    
    def username(self, obj):
        return obj.user.username
    username.short_description = 'Username'
