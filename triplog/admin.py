from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ExportMixin
from .models import Driver, Product, Route, Trip, TripProduct, TripRoute, Truck, TruckCompany
from .resources import TripResource, TruckResource, DriverResource, RouteResource, TripProductResource, TripRouteResource, TruckCompanyResource, ProductResource

class TripRouteInline(admin.TabularInline):
    model = TripRoute
    extra = 0
    readonly_fields = ('actual_time_min',)  # Make calculated field read-only

# @admin.register(Trip)

class TripAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TripResource
    inlines = [TripRouteInline]
    inlines = [TripRouteInline]
    list_display = ('truck', 'driver', 'departure_time', 'arrival_time', 'status')
    list_editable = ('arrival_time', 'status')
    search_fields = ('truck__plate_number', 'driver__name', 'status', 'clerk__username')

class DriverAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = DriverResource
    list_display = [
        "name",
        "assigned_truck",
        "contact",
    ]
    search_fields = ('name',)

class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ProductResource
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
    search_fields = ('plate_number','truck_company')

class TripProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TripProductResource
    search_fields = ('trip__id', 'product__name')

class TripRouteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TripRouteResource
    search_fields = ('trip__id', 'route__origin','route__destination')

class TruckCompanyAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TruckCompanyResource
    search_fields = ('name',)


# Register your models here.
admin.site.register(Driver, DriverAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Truck, TruckAdmin)
admin.site.register(TruckCompany, TruckCompanyAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(TripProduct, TripProductAdmin)
admin.site.register(TripRoute, TripRouteAdmin)
