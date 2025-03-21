from django.contrib import admin
from .models import Driver, Product, Route, Trip, TripProduct, TripRoute, Truck, TruckCompany

class DriverAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "assigned_truck",
        "contact",
    ]

class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
    ]

class RouteAdmin(admin.ModelAdmin):
    list_display = [
        "origin",
        "destination",
        "distance_km",
    ]

class TruckAdmin(admin.ModelAdmin):
    list_display = [
        "plate_number",
        "truck_company",
        "capacity_kg"
    ]

# Register your models here.
admin.site.register(Driver, DriverAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Truck, TruckAdmin)
admin.site.register(TruckCompany)
admin.site.register(Trip)
admin.site.register(TripProduct)
admin.site.register(TripRoute)
