from import_export import resources
from .models import Trip, Truck, Driver, Route, TripProduct, TripRoute, TruckCompany, Product

class TripResource(resources.ModelResource):
    class Meta:
        model = Trip
        import_id_fields = ('id',)  # Use 'id' to match records when importing

class TruckResource(resources.ModelResource):
    class Meta:
        model = Truck
        import_id_fields = ('id',)  # Use 'id' to match records when importing

class DriverResource(resources.ModelResource):
    class Meta:
        model = Driver
        import_id_fields = ('id',)  # Use 'id' to match records when importing

class RouteResource(resources.ModelResource):
    class Meta:
        model = Route
        import_id_fields = ('id',)  # Use 'id' to match records when importing

class TripProductResource(resources.ModelResource):
    class Meta:
        model = TripProduct
        import_id_fields = ('id',)  # Use 'id' to match records when importing

class TripRouteResource(resources.ModelResource):
    class Meta:
        model = TripRoute
        import_id_fields = ('id',)  # Use 'id' to match records when importing

class TruckCompanyResource(resources.ModelResource):
    class Meta:
        model = TruckCompany
        import_id_fields = ('id',)  # Use 'id' to match records when importing

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        import_id_fields = ('id',)  # Use 'id' to match records when importing