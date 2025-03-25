from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ExportMixin
from .models import Driver, Product, Route, Trip, TripProduct, TripRoute, Truck, TruckCompany
from .resources import TripResource, TruckResource, DriverResource, RouteResource, TripProductResource, TripRouteResource

class TripAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TripResource

class DriverAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = DriverResource
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

class RouteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = RouteResource
    list_display = [
        "origin",
        "destination",
        "distance_km",
    ]

class TruckAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TruckResource
    list_display = [
        "plate_number",
        "truck_company",
        "capacity_kg"
    ]

class TripProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TripProductResource

class TripRouteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TripRouteResource

# Register your models here.
admin.site.register(Driver, DriverAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Truck, TruckAdmin)
admin.site.register(TruckCompany)
admin.site.register(Trip, TripAdmin)
admin.site.register(TripProduct, TripProductAdmin)
admin.site.register(TripRoute, TripRouteAdmin)
