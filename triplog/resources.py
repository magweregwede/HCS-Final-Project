from import_export import resources
from .models import Trip, Truck, Driver, Route, TripProduct, TripRoute

class TripResource(resources.ModelResource):
    class Meta:
        model = Trip

class TruckResource(resources.ModelResource):
    class Meta:
        model = Truck

class DriverResource(resources.ModelResource):
    class Meta:
        model = Driver

class RouteResource(resources.ModelResource):
    class Meta:
        model = Route

class TripProductResource(resources.ModelResource):
    class Meta:
        model = TripProduct

class TripRouteResource(resources.ModelResource):
    class Meta:
        model = TripRoute